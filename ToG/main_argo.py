from tqdm import tqdm
import argparse
import random
from argo_func import *
from client import *
from utils import *

import json

from dotenv import load_dotenv
import os

import json
from arango import ArangoClient
from langchain_community.graphs import ArangoGraph

# change tenant_id

# Load the .env file
load_dotenv()

# -*- coding: utf-8 -*-

if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--dataset", type=str,
    #                     default="webqsp", help="choose the dataset.")
    # parser.add_argument("--max_length", type=int,
    #                     default=256, help="the max length of LLMs output.")
    # parser.add_argument("--temperature_exploration", type=float,
    #                     default=0.4, help="the temperature in exploration stage.")
    # parser.add_argument("--temperature_reasoning", type=float,
    #                     default=0, help="the temperature in reasoning stage.")
    # parser.add_argument("--width", type=int,
    #                     default=3, help="choose the search width of ToG.")
    # parser.add_argument("--depth", type=int,
    #                     default=3, help="choose the search depth of ToG.")
    # parser.add_argument("--remove_unnecessary_rel", type=bool,
    #                     default=True, help="whether removing unnecessary relations.")
    # parser.add_argument("--LLM_type", type=str,
    #                     default="gpt-3.5-turbo", help="base LLM model.")
    # parser.add_argument("--opeani_api_keys", type=str,
    #                     default="", help="if the LLM_type is gpt-3.5-turbo or gpt-4, you need add your own openai api keys.")
    # parser.add_argument("--num_retain_entity", type=int,
    #                     default=5, help="Number of entities retained during entities search.")
    # parser.add_argument("--prune_tools", type=str,
    #                     default="llm", help="prune tools for ToG, can be llm (same as LLM_type), bm25 or sentencebert.")
    # parser.add_argument("--addr_list", type=str,
    #                     default="server_urls.txt", help="The address of the Wikidata service.")
    # args = parser.parse_args()

    args_dict = {
        "dataset": "fci",
        "max_length": 256,
        "temperature_exploration": 0.4,
        "temperature_reasoning": 0,
        "width": 3,
        "depth": 5,
        "remove_unnecessary_rel": True,
        "LLM_type": "gpt-4o-mini",
        "opeani_api_keys": os.getenv("OPENAI_API_KEY"),
        "num_retain_entity": 5,
        "prune_tools": "llm",
        "addr_list": "F:\\CodingEnvironment\\tog\\ToG\\server_urls.txt"
    }

    args = argparse.Namespace(**args_dict)

        
    datas, question_string = prepare_dataset(args.dataset)
    print("Start Running ToG on %s dataset." % args.dataset)
    for i in tqdm(range(6,len(datas))):
        question = datas[question_string][i]
        topic_entity = extract_entity_question(question,args)
        cluster_chain_of_entities = []
        if len(topic_entity) == 0:
            results = generate_without_explored_paths(question, args)
            save_2_jsonl(question, results, [], file_name=args.dataset)
            continue
        pre_relations = []
        pre_heads= [-1] * len(topic_entity)
        flag_printed = False

        tenant_id = 'ke'
        NODE_COLLECTION = 'nodes'
        RELATIONSHIP_COLLECTION = 'relationships'

        client = ArangoClient(hosts='http://localhost:8529')

        sys_db = client.db(
            '_system',
            username = 'root',
            password = ''
        )

        db = client.db(tenant_id)
        graph_db = ArangoGraph(db)
        client = graph_db

        finish = []

        for depth in range(1, args.depth+1):
            away_all = {}
            current_entity_relations_list = []
            i=0
            for entity in topic_entity:
                if entity not in finish:
                    print("Entity: ", entity)
                    # try:
                    try:

                        print(pre_heads, i)
                        retrieve_relations_with_scores, away = relation_search_prune(entity, pre_relations, pre_heads[i], question, args, client)  # @best entity triplet, entitiy_id
                        current_entity_relations_list.extend(retrieve_relations_with_scores)
                        finish.append(entity)

                        for key in away:
                            if key not in away_all:
                                away_all[key] = away[key]
                    
                    except:
                        # raise Exception("stop")
                        break
                i+=1
            total_candidates = []
            total_scores = []
            total_relations = []
            total_entities_id = []
            total_topic_entities = []
            total_head = []

            print("curent entity: ",current_entity_relations_list)
            # raise Exception("Stop here")

            new_current = []
            for key in away_all:
                new_current.append((key, away_all[key]))
                
            if True:
                stop, results = new_reasoning(question, new_current, args)
                if stop:
                    print("ToG stoped at depth %d." % depth)
                    save_2_jsonl(question, results, new_current, file_name=args.dataset)
                    flag_printed = True
                    break #@
                    # raise Exception("stop")

            for entity in current_entity_relations_list:
                value_flag=False
                
                entity_candidates = entity_search(entity['entity'], entity['relation'], client, entity['head']) #@

                scores, entity_candidates = entity_score(question, entity_candidates, entity['score'], entity['relation'], args)
                
                total_candidates, total_scores, total_relations, total_topic_entities, total_head = update_history(entity_candidates, entity, scores, total_candidates, total_scores, total_relations, total_topic_entities, total_head, value_flag)

            # raise Exception("stop")

            if len(total_candidates) ==0:
                half_stop(question, cluster_chain_of_entities, depth, args)
                flag_printed = True
                break #
                raise Exception("stop")
                
            flag, chain_of_entities, pre_relations, pre_heads = entity_prune( total_relations, total_candidates, total_topic_entities, total_head, total_scores, args, client) #@
            cluster_chain_of_entities.append(chain_of_entities)
            print("cluster_chain_of_entities: ", cluster_chain_of_entities)
            if flag:
                stop, results = reasoning(question, cluster_chain_of_entities, args)
                if stop:
                    print("ToG stoped at depth %d." % depth)
                    save_2_jsonl(question, results, cluster_chain_of_entities, file_name=args.dataset)
                    flag_printed = True
                    break
                    raise Exception("stop")
                else:
                    print("depth %d still not find the answer." % depth)
                    # flag_finish, entities_id = if_finish_list(entities_id)
                    # if flag_finish:
                    #     half_stop(question, cluster_chain_of_entities, depth, args)
                    #     flag_printed = True
                    # else:
                    for candidate in total_candidates:
                        if candidate not in topic_entity:
                            topic_entity.append(candidate)

                    temp = []
                    for entity in topic_entity:
                        if entity not in temp:
                            temp.append(entity)
                    topic_entity = temp
                    
                    continue #
                    raise Exception("stop")
            else:
                half_stop(question, cluster_chain_of_entities, depth, args)
                flag_printed = True
        
        if not flag_printed:
            results = generate_without_explored_paths(question, args)
            save_2_jsonl(question, results, [], file_name=args.dataset)
