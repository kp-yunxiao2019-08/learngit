'''
author: wukai@aiyunxiao.com
date: 2020/02/06

评估场景：
  1. 直接评估搜索引擎的召回效果
  2. 修改搜索引擎内部逻辑，需要更换配置中搜索引擎地址为测试地址
'''
import os
import re
import sys
import json
import urllib
import urllib.request
import urllib.parse
import threading
import logging
from datetime import datetime
from queue import Empty
from functools import cmp_to_key

from tasks.dber.dber import MongoDBer
from tasks.search_sphinx import Sphinx
from conf.flows_debug import search_sphinx, search_sphinx_priority
from conf.databases import DATABASES
from sam_ques_search_settings import SETTINGS

# TODO 找到每张试卷ctime及每道推荐原题的ctime，比对得出哪些是新创建的试题


re_nbsp = re.compile(r'(?:&nbsp;?)+')
head_remove = re.compile(r'^.{0,50}?\d{1,2}[}$]{0,2}分.(?!(?:<br/?>)){0,50}?<br>(\d{1,2}(?:、|\.|．|·|，|,))')
score_remove = re.compile(r'(?:（|\()[^）\)\(（]*\d{1,2}[}$]{0,2}分[^\(（）\)]*(?:）|\))')
mark_re = re.compile(r'</?[^>]+>')
ques_num_re = re.compile(r'^\d{1,2}(?:、|\.|．|·|，|,)')
option_re = re.compile(r'[A-Dc](．|·|\.|,|，|、)+')

def _query_text_trans(query):
    """用于ocr文本展示的去噪
    """
    query = re_nbsp.sub(' ', query)
    if '分' in query[:100]:
        query = head_remove.sub(r'\1', query)
    query = score_remove.sub('', query)
    return query

def _query_transform(query):
    """query字符串去噪
    """
    query = _query_text_trans(query)
    query = mark_re.sub('', query)
    query = ques_num_re.sub('', query)
    query = option_re.sub(' ',query)
    return query

def get_questions_url(url_list, retry_times=3):
    '''元培中image uri转换为url
    '''
    data = {}
    if isinstance(url_list, str):
        url_list = [url_list]
    data['uris'] = url_list
    url = 'http://kb-ks.yunxiao.com/yuanpei_api/v1/questions/urls/?api_key=iyunxiao_kb_yuanpei'
    data_arg = json.dumps(data, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=data_arg)
    req.add_header("Content-Type", "application/json")
    for _ in range(retry_times):
        try:
            resp = request.urlopen(req, timeout=30)
            content = resp.read()
            url_d = json.loads(content)
            if u'code' in url_d:
                continue
            url_list = url_d['urls']
            return url_list
        except Exception:
            continue

    #raise Exception('Error: _get_questions_url:over retry times: %s' %
    #                url)

def get_sphinx():
    '''
    通过引用，返回元培的搜索模块
    '''
    kwargs = search_sphinx_priority['kwargs']
    kwargs['db'] = MongoDBer(search_sphinx_priority['args'][1])
    kwargs['str_punish'] = kwargs.pop('punish')
    kwargs['know_ration'] = kwargs.pop('str_threshold')
    kwargs['query_threshold'] = kwargs.pop('query_dis')
    kwargs['logger'] = logging.getLogger(search_sphinx_priority['args'][0])
    kwargs['yuanpei_api'] = {'host':'http://kb-ks.yunxiao.com', 'kb_api_key':{'api_key':'iyunxiao_kb_yuanpei'}}

    sphinx = Sphinx(**kwargs)
    return sphinx

def get_ques_ids(cond, ques_count, db_read_mkp, db_read_yp):
    '''
    获取要评估的试题id
    '''
    if '_id' in cond:
        ques_ids = [cond['_id']]
    else:
        paper_ids = []
        ques_ids = []
        proj = {'g_paper_id': 1, 'questions': 1, 'subject': 1}
        with db_read_mkp['yp_exampaper'].find(cond, proj, no_cursor_timeout=True) as cursor:
            for one_exam in cursor:
                g_paper_id = one_exam['g_paper_id']
                paper_ids.append(g_paper_id)
                questions = one_exam['questions']
        with db_read_yp['paper'].find({'_id': {'$in': paper_ids}}, no_cursor_timeout=True) as cursor:
            for one_exam in cursor:
                subject = one_exam['subject'] 
                #ques_ids = sub_ques_d.setdefault(subject, []) 
                for block in one_exam['blocks']:
                    for question in block['questions']:
                        ques_ids.append(question['id'])
    if ques_count:
        ques_ids = ques_ids[:ques_count]
    print('评估试题数: %s' % len(ques_ids))
    return ques_ids

def gen_sam_ques_id_map(db_read_yp, ques_ids):
    '''
    生成试题_id与标注原题_id的映射关系
    '''
    sam_ques_id_map = {}
    bulk = [] 
    for qid in ques_ids:
        bulk.append(qid)
        if len(bulk) >= 100:
            with db_read_yp.question.find({'_id': {'$in': bulk}}) as cursor:
                for data in cursor:
                    ques_id = data['_id']
                    sam_ques_id = data.get('human_mark', {}).get('kb_ques_id')
                    if not sam_ques_id or 'text' not in data['ai_mark']:
                        continue
                    reco_ques_ids = [x['id'] for x in data['ai_mark'].get('reco_questions', [])]
                    text = data['ai_mark']['text']
                    image_url = data['image_url']
                    sam_ques_id_map[ques_id] = {
                        'sam_ques_id': sam_ques_id,
                        'reco_ques_ids': reco_ques_ids,
                        'ocr_text': text,
                        'image_url': image_url,
                        'subject': data['subject']
                    }
            bulk = []
    if bulk:
        with db_read_yp.question.find({'_id': {'$in': bulk}}) as cursor:
            for data in cursor:
                ques_id = data['_id']
                sam_ques_id = data.get('human_mark', {}).get('kb_ques_id')
               #if not sam_ques_id or 'text' not in data['ai_mark']:
               #    continue
                reco_ques_ids = [x['id'] for x in data['ai_mark'].get('reco_questions', [])]
                text = data['ai_mark'].get('text', '') or data['ai_mark'].get('ori_text', '')
                image_url = data['image_url']
                sam_ques_id_map[ques_id] = {
                    'sam_ques_id': sam_ques_id,
                    'reco_ques_ids': reco_ques_ids,
                    'ocr_text': text,
                    'image_url': image_url,
                    'subject': data['subject']
                }
    return sam_ques_id_map

def search(sphinx, ques_ids):
    sphinx.g_ques_id_list = ques_ids
    threads = []
    t = threading.Thread(target=sphinx._thread_search_producer, args=())
    t.setDaemon(True)
    t.start()
    threads.append(t)

    for _ in range(sphinx.thread_search_num):
        t = threading.Thread(target=sphinx._thread_search_consumer, args=())
        t.setDaemon(True)
        t.start()
        threads.append(t)

    return threads

def statis(es_host, sam_ques_id_map, badcase_id_file, kb_db, extra_info_file=None):
    statis_all = {}
    print_count = 0
    print_search_none = 0
    for id_, info in sam_ques_id_map.items():
        try:
            host = es_host
            subject_ = info.get('subject')
            params = {
                'limit': '30', # limit 结果限制条数
                'excerpt': '0', # 飘红，0为不飘红
                'min_num': '10', # 最少结果显示，会放宽搜索条件
                #'query_field': 'stem',
                'api_key': 'iyunxiao_haofenshu8361',
            }
            if subject_:
                params['subject'] = subject_
            params['query'] = _query_transform(info['ocr_text'])
            params_encode = urllib.parse.urlencode(params)
            url = host + '?' + params_encode
            req = urllib.request.Request(url)
            handle = urllib.request.urlopen(req, timeout=60)
            search_data = json.loads(handle.read())
            search_result = search_data['data']['docs']
        except Exception as err:
            search_result = None
        if not search_result:
            print_search_none += 1
        else:
            try:
                print_count += 1
                print('count: %s' % print_count)
                yp_ques_id = id_
                sam_ques_id = sam_ques_id_map[yp_ques_id]['sam_ques_id']
                reco_ques_ids = sam_ques_id_map[yp_ques_id]['reco_ques_ids']
                ocr_text = sam_ques_id_map[yp_ques_id]['ocr_text']
                #print(ocr_text, file=extra_info_file)
                image_url = sam_ques_id_map[yp_ques_id]['image_url']
                subject = sam_ques_id_map[yp_ques_id]['subject']
                new_reco_ques_ids_ = [s['id'] for s in search_result]
                #new_reco_ques_ids = new_reco_ques_ids_[:1]
                new_reco_ques_ids = new_reco_ques_ids_[:10]
                statis_single = statis_all.setdefault(subject, {})
                statis_single.setdefault('all_count', 0)
                statis_single.setdefault('ori_sam_count', 0)
                statis_single.setdefault('new_sam_count', 0)
                statis_single.setdefault('index', 0)

                statis_single['all_count'] = statis_single['all_count'] + 1
                if sam_ques_id and sam_ques_id in reco_ques_ids:
                    statis_single['ori_sam_count'] = statis_single['ori_sam_count'] + 1
                if sam_ques_id and sam_ques_id in new_reco_ques_ids:
                    statis_single['new_sam_count'] = statis_single['new_sam_count'] + 1
                    statis_single['index'] = statis_single['index'] + new_reco_ques_ids.index(sam_ques_id)
                elif sam_ques_id:
                    print(new_reco_ques_ids_)
                    print(yp_ques_id, file=badcase_id_file)
                    print(get_questions_url(image_url))
                    print('yp_ques_id: %s, sam_ques_id: %s, ocr_text: %s, reco_ques_ids: %s' % (yp_ques_id, sam_ques_id, ocr_text, reco_ques_ids))
                    with kb_db.question.find({'_id': {'$in': reco_ques_ids[:10]}}) as cursor:
                        for data in cursor:
                            print(data['blocks']['stems'])
                else:
                    print('未标注原题: %s' % yp_ques_id, file=sys.stderr)
            except Exception as err:
                print(err)
    for subject_, statis_single in statis_all.items():
        print('学科：%s' % subject_)
        if statis_single['all_count']:
            print('统计错题本试题总数: %s' % statis_single['all_count'])
            print('已标注错题本原题率: %s%%' % round(statis_single['ori_sam_count']/statis_single['all_count']*100, 2))
            print('优化后预计原题率: %s%%' % round(statis_single['new_sam_count']/statis_single['all_count']*100, 2))
            if statis_single['new_sam_count']:
                print('优化后平均位置: %s' % (statis_single['index'] / statis_single['new_sam_count']))

def parse_params():
    '''
    解析输入参数，获得查询条件及初始化相关sphinx属性
    '''
    params = sys.argv
    mode = params[1]
    mode_settins = SETTINGS[mode]
    ques_count = mode_settins.get('ques_count', None)
    if len(params) > 2:
        if mode == 'iterate':
            debug_id = params[2]
            cond = {'_id': debug_id}
        else:
            debug_file = params[2]
            debug_ids = []
            with open(debug_file) as f:
                for line in f:
                    debug_ids.append(line.strip())
            cond = {'_id': debug_ids}
    else:
        cond = {'is_ctb_paper': True, 'status': 'digitized', 'markinfo.mark_type': 'digitize'}
        period_l = mode_settins.get('period_l', None)
        subject_l = mode_settins.get('subject_l', None)
        start_time = mode_settins.get('start_time', None)
        end_time = mode_settins.get('end_time', None)
        if period_l:
            cond['period'] = {'$in': period_l}
        if subject_l:
            cond['subject'] = {'$in': subject_l}
        if start_time or end_time:
            cond['ctime'] = {}
            if start_time:
                cond['ctime']['$gt'] = datetime(*list(map(int, start_time.split('-'))))
            if end_time:
                cond['ctime']['$lt'] = datetime(*list(map(int, end_time.split('-'))))
    return cond, ques_count
    
def main():
    badcase_id_file_path = '%s_%s' % (sys.argv[1], datetime.now().strftime('%Y_%m%d'))
    badcase_id_file_path = badcase_id_file_path + '_' + '理科去题型'
    if 'badcase' in badcase_id_file_path and os.path.exists(badcase_id_file_path):
        #raise Exception('badcase文件已存在: %s, 请另存！' % badcase_id_file_path)
        print('badcase文件已存在: %s, 请另存！' % badcase_id_file_path)
    badcase_id_file = open(badcase_id_file_path, 'w')
    extra_info_file = open('test_text', 'w')
    # 新逻辑
    db_read = MongoDBer(DATABASES['kb_online'])
    db_read_mkp = MongoDBer(DATABASES['mkp_online'])
    db_read_yp = MongoDBer(DATABASES['yuanpei_online'])
    cond, ques_count = parse_params()
    mode_settins = SETTINGS[sys.argv[1]]
    es_host = mode_settins.get('es_host', 'http://kb-ks.yunxiao.com/se_kb/v2/search/questions')
    ques_ids = get_ques_ids(cond, ques_count, db_read_mkp, db_read_yp)
    sam_ques_id_map = gen_sam_ques_id_map(db_read_yp, ques_ids)
    ques_ids = list(sam_ques_id_map.keys())

    statis(es_host, sam_ques_id_map, badcase_id_file, db_read, extra_info_file)
    badcase_id_file.close()
    extra_info_file.close()
    
if __name__ == '__main__':
    main()
