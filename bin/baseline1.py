#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys,os,argparse,shutil,glob,json,copy,time
#import simplejson as json

SLOTS = ['kind','menu','material']

def main(argv):
    #
    # CMD LINE ARGS
    # 
    install_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    utils_dirname = os.path.join(install_path,'lib')
    sys.path.append(utils_dirname)
    from dataset_walker import dataset_walker
    list_dir = os.path.join(install_path,'config')
    print "list_dir=%s" %(list_dir)

    parser = argparse.ArgumentParser(description='Simple hand-crafted dialog state tracker baseline.')
    parser.add_argument('--dataset', dest='dataset', action='store', metavar='DATASET', required=True,
                        help='The dataset to analyze, for example train1 or test2 or train3a')
    parser.add_argument('--dataroot',dest='dataroot',action='store',required=True,metavar='PATH',
                        help='Will look for corpus in <destroot>/<dataset>/...')
    parser.add_argument('--trackfile',dest='scorefile',action='store',required=True,metavar='JSON_FILE',
                        help='File to write with tracker output')
    parser.add_argument('--null',dest='null',action='store_true',
                        help='Always output "None of the above" for all slots with score 1.0')
    parser.add_argument('--ignorescores',dest='ignorescores',action='store_true',
                        help='Ignore score in data; always use a score of 1.0 (nop if --null also specified)')
    args = parser.parse_args()
    print "args.dataset=%s args.dataroot=%s" %(args.dataset, args.dataroot)

    sessions = dataset_walker(args.dataset,dataroot=args.dataroot,labels=False)    
    start_time = time.time()
    r = {
        'sessions': [],
        'dataset': args.dataset,
        }
    
    for session in sessions:
        print "sessions=%s" %(session)
        string= raw_input("json형식으로 입력해주세요\n")
        #string = sys.stdin.readlines()
        #print("입력내용"+str)
        
        session.log=json.loads(string)
        r['sessions'].append( { 'turns': [], 'session-id': session.log['session-id'], } )
        state = _InitState()        
        if (args.null == True):
            state['joint'] = { 'hyps': [], }
        print "trun_index=0"
        #string = raw_input("턴 내용을 json형식으로 입력해주세요\n")
        print "턴 내용을 json형식으로 입력해주세요"
        string = sys.stdin.readlines()
        #dictb=json.loads(string)
        #dicta={'turns':[]}
        dictb={'turns':[]}
        dicta=json.dumps(string)
        dictb['turns'].append(json.loads(dicta))
        print "dump= %s" %(json.dumps(dictb))
        dictc=json.dumps(dictb)
        dictd=json.loads(dictc)
        print "dictd=%s\n" %(dictd)
        print dictd['turns']['output']
        for item in dictb:
           print "item=%s" %(item)
           if item['turns']:
                 e = item['turns']
                 for k,value in e.items():
                         if k == "youtube":
                              for innerk, innerv in k.iteritems():
                                     if innerk == "source":
                                            print innerv
                         print e
        for each_dict in value:
                 for innerk, innerv in each_dict.iteritems():
                            if innerk == "source" :
                                    print innerv
        for k,v in dictb.items():
            merge(session.log.setdefault(k, []), v)
        print session.log
        for turn_index,(log_turn,scratch) in enumerate(session):
            #print "trun_index=%s" %(turn_index)
            #string = raw_input("턴 내용을 json형식으로 입력해주세요 \n")

            #session.log+=json.loads(string)

            if (args.null == True):
                r['sessions'][-1]['turns'].append(state)
                continue
            # check whether to initialize state or copy
            if (log_turn['restart'] == True or turn_index == 0):
                state = _InitState()
            else:
                state = copy.deepcopy(state)
            r['sessions'][-1]['turns'].append(state)
            print " **log_trun[input][live][slu_hyps]=%s" %(log_turn['input']['live']['slu-hyps'])
            if (len(log_turn['input']['live']['slu-hyps']) == 0):
                # no recognition results; skip
                continue
            slu_hyp = log_turn['input']['live']['slu-hyps'][0]
            joint = {}
            joint_scores = []            
            for slot in SLOTS:
                for act_hyp in slu_hyp['slu-hyp']:
                    this_pairset = {}
                    for found_slot,val in act_hyp['slots']:
                        if (found_slot.startswith(slot)):
                            this_pairset[found_slot] = val
                            print "   this_pairset[%s]=%s act_hyp[%s]=%s" %(found_slot, val, slot, act_hyp['slots'])
                    if (len(this_pairset) == 0):
                        continue
                    if (len(state[slot]['hyps']) == 0 or state[slot]['hyps'][0]['score-save'] < slu_hyp['score']):
                        score = slu_hyp['score'] if (args.ignorescores == False) else 1.0
                        state[slot]['hyps'] = [ {
                                'score-save': slu_hyp['score'],
                                'score': score,
                                'slots': this_pairset,
                                } ]
                if (len(state[slot]['hyps']) > 0):
                    print "   len(state[%s]['hyps'])=%d" %(slot,len(state[slot]['hyps']))
                    print "   state[%s]['hyps'][0]['score']=%s" %(slot,state[slot]['hyps'][0]['score'])
                    joint_scores.append( state[slot]['hyps'][0]['score'] )
                    for (my_slot,my_val) in state[slot]['hyps'][0]['slots'].items():
                        joint[my_slot] = my_val
            state['joint'] = { 'hyps': [], }
            if (len(joint_scores) > 0):
                state['joint']['hyps'].append( {
                        'score': sum(joint_scores) / len(joint_scores),
                        'slots': joint,
                        } )
                print "  state['joint']['hyps']=%s" %(state['joint']['hyps'])

            print "trun_index=%s" %(turn_index)
            string = raw_input("턴 내용을 json형식으로 입력해주세요 \n")

            dictb=json.loads(string)

            for k,v in dictb.items():
                  merge(session.log.setdefault(k, []), v)

        for turn in r['sessions'][-1]['turns']:
            print " trun in r =%s" %(turn)
            for slots_entry in turn.values():
                for hyp_entry in slots_entry['hyps']:
                    if ('score-save' in hyp_entry):
                        del hyp_entry['score-save']
    end_time = time.time()
    elapsed_time = end_time - start_time
    r['wall-time'] = elapsed_time
    #print state
    #print joint

    f = open(args.scorefile,'w')
    print "args.scorefile=%s" %(args.scorefile)
    json.dump(r,f,indent=2)
    f.close()

def _InitState():
    state = {}
    for slot in SLOTS:
        state[slot] = {'hyps': [], }    
    return state

if (__name__ == '__main__'):
    main(sys.argv)


def merge(lsta, lstb):
    for i in lstb:
        for j in lsta:
             if j['name'] == i['name']:
                  j.update(i)
                  break
        else:
             lsta.append(i)
