'''
author: wukai@aiyunxiao.com
date: 2020/02/06

将此脚本置于yuanpei项目下直接执行即可进行评估
===========
评估场景：
  1. 修改元培搜索标注逻辑，直接评估即可
  2. 修改搜索引擎内部逻辑，需要更换配置中搜索引擎地址为测试地址
'''
import os
import sys
import json
from urllib import request
import threading
import logging
from datetime import datetime
from queue import Empty

from tasks.dber.dber import MongoDBer
from tasks.search_sphinx import Sphinx
from conf.flows_debug import search_sphinx, search_sphinx_priority
from sam_ques_search_settings import SETTINGS

# TODO 找到每张试卷ctime及每道推荐原题的ctime，比对得出哪些是新创建的试题

def get_questions_url(url_list, retry_times=3):
    '''元培中image uri转换为url
    '''
    data = {}
    if isinstance(url_list, str):
        url_list = [url_list]
    data['uris'] = url_list
    url = 'http://kb-ks.yunxiao.com/yuanpei_api/v1/questions/urls/?api_key=iyunxiao_kb_yuanpei'
    data_arg = json.dumps(data, ensure_ascii=False).encode('utf-8')
    req = request.Request(url, data=data_arg)
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

    raise Exception('Error: _get_questions_url:over retry times: %s' %
                    url)

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

    sphinx = Sphinx(**kwargs)
    return sphinx

def get_ques_ids(sphinx, cond, ques_count):
    '''
    获取要评估的试题id
    '''
    ques_ids = []
    if '_id' in cond:
        if isinstance(cond['_id'], list):
            ques_ids.extend(cond['_id'])
        else:
            ques_ids.append(cond['_id'])
    else:
        proj = {'questions': 1, 'ctime': 1, 'publish_time': 1}
        with sphinx.coll_exam.find(cond, proj) as cursor:
            for one_exam in cursor:
                questions = one_exam['questions']
                for one_ques in questions:
                    yp_ques_id = one_ques['g_question_id']
                    ques_ids.append(yp_ques_id)
    if ques_count:
        ques_ids = ques_ids[:ques_count]
    print('评估试题数: %s' % len(ques_ids))
    return ques_ids

def gen_sam_ques_id_map(sphinx, ques_ids):
    '''
    生成试题_id与标注原题_id的映射关系
    '''
    sam_ques_id_map = {}
    bulk = [] 
    for qid in ques_ids:
        bulk.append(qid)
        if len(bulk) >= 100:
            with sphinx.coll_ques.find({'_id': {'$in': bulk}}) as cursor:
                for data in cursor:
                    ques_id = data['_id']
                    reco_mark = data.get('recognization', {}) or data.get('mark', {})
                    sam_ques_id = data.get('mark', {}).get('sam_kb_ques_id')
                    if not sam_ques_id:
                        continue
                    reco_ques_ids = [x['id'] for x in reco_mark.get('reco_questions', [])]
                    text = data['recognization']['text']
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
        with sphinx.coll_ques.find({'_id': {'$in': bulk}}) as cursor:
            for data in cursor:
                ques_id = data['_id']
                reco_mark = data.get('recognization', {}) or data.get('mark', {})
                sam_ques_id = data.get('mark', {}).get('sam_kb_ques_id')
                if not sam_ques_id:
                    continue
                reco_ques_ids = [x['id'] for x in reco_mark.get('reco_questions', [])]
                text = data['recognization']['text']
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

    print(sphinx.thread_search_num)
    for _ in range(sphinx.thread_search_num):
        t = threading.Thread(target=sphinx._thread_search_consumer, args=())
        t.setDaemon(True)
        t.start()
        threads.append(t)

    return threads

def statis(sphinx, sam_ques_id_map, badcase_id_file, kb_db, extra_info_file=None):
    statis_all = {}
    print_count = 0
    while True:
        try:
            search_result = sphinx.search_q.get(timeout=300)
        except Empty:
            continue
        if not search_result:
            sphinx.print_search_none += 1
            if sphinx.print_search_none == sphinx.thread_search_num:
                if search_result is None:
                    sphinx.search_q.task_done()
                break
            else: pass
        else:
            try:
                print_count += 1
                print('count: %s' % print_count)
                yp_ques_id = search_result['_id']
                sam_ques_id = sam_ques_id_map[yp_ques_id]['sam_ques_id']
                reco_ques_ids = sam_ques_id_map[yp_ques_id]['reco_ques_ids']
                ocr_text = sam_ques_id_map[yp_ques_id]['ocr_text']
                print(ocr_text, file=extra_info_file)
                image_url = sam_ques_id_map[yp_ques_id]['image_url']
                subject = sam_ques_id_map[yp_ques_id]['subject']
                new_reco_ques_ids = [x['id'] for x in search_result['recognization']['reco_questions']]
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
            finally:
                sphinx.search_q.task_done()
    for subject_, statis_single in statis_all.items():
        print('学科：%s' % subject_)
        if statis_single['all_count']:
            print('统计错题本试题总数: %s' % statis_single['all_count'])
            print('已标注错题本原题率: %s%%' % round(statis_single['ori_sam_count']/statis_single['all_count']*100, 2))
            print('优化后预计原题率: %s%%' % round(statis_single['new_sam_count']/statis_single['all_count']*100, 2))
            if statis_single['new_sam_count']:
                print('优化后平均位置: %s' % (statis_single['index'] / statis_single['new_sam_count']))

def parse_params(sphinx):
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
        cond = {'is_ctb_paper': True, 'status': 'human_marked', 'is_master': 1, 'valid': True}
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
    es_host = mode_settins.get('es_host', None) 
    if es_host:
        sphinx.serv_host = es_host
    return cond, ques_count
    
def main():
    badcase_id_file_path = '%s_%s' % (sys.argv[1], datetime.now().strftime('%Y_%m%d'))
    badcase_id_file_path = badcase_id_file_path + '_' + '理科去题型'
    if 'badcase' in badcase_id_file_path and os.path.exists(badcase_id_file_path):
        raise Exception('badcase文件已存在: %s, 请另存！' % badcase_id_file_path)
    badcase_id_file = open(badcase_id_file_path, 'w')
    extra_info_file = open('test_text', 'w')
    sphinx = get_sphinx()
    sphinx.db = MongoDBer('mongodb://kb_read:Apz6O6qYY7oAi98P@10.10.200.132:6010/kb_yuanpei')
    kb_db = MongoDBer('mongodb://kb_read:VexX7HFqXqeAfjOz@10.10.200.112:6010/kb')
    sphinx.coll_ques = sphinx.db.question
    sphinx.coll_exam = sphinx.db.exampaper
    cond, ques_count = parse_params(sphinx)
    ques_ids = get_ques_ids(sphinx, cond, ques_count)
    sam_ques_id_map = gen_sam_ques_id_map(sphinx, ques_ids)
    ques_ids = list(sam_ques_id_map.keys())
    threads = search(sphinx, ques_ids) 
    statis(sphinx, sam_ques_id_map, badcase_id_file, kb_db, extra_info_file)
    for thread in threads:
        thread.join()
    badcase_id_file.close()
    extra_info_file.close()
    
if __name__ == '__main__':
    main()
