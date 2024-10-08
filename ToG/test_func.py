from prompt_list_vi import *
import json
import openai
import re
import time
from utils import *

def extract_entity_question(question, args):
    prompt = extract_question_entity + question

    response = run_llm(prompt, args.temperature_reasoning, args.max_length, args.opeani_api_keys, args.LLM_type)
    
    result = extract_answer(response)
    
    entities_list = [entity.strip() for entity in re.split(r',\s*', result) if entity]

    # print(entities_list)
    # raise Exception("stop")
    return entities_list

def transform_relation(relation):
    relation_without_prefix = relation.replace("wiki.relation.", "").replace("_", " ")
    return relation_without_prefix


def clean_relations(string, entity_id, head_relations):
    pattern = r"{\s*(?P<relation>[^()]+)\s+\(Score:\s+(?P<score>[0-9.]+)\)}"
    relations=[]
    for match in re.finditer(pattern, string):
        relation = match.group("relation").strip()
        relation = transform_relation(relation)
        if ';' in relation:
            continue
        score = match.group("score")
        if not relation or not score:
            return False, "output uncompleted.."
        try:
            score = float(score)
        except ValueError:
            return False, "Invalid score"
        if relation in head_relations:
            relations.append({"entity": entity_id, "relation": relation, "score": score, "head": True})
        else:
            relations.append({"entity": entity_id, "relation": relation, "score": score, "head": False})
    if not relations:
        return False, "No relations found"
    return True, relations


def new_clean_relations(string, entity_id, head_relations, relationship):
    pattern = r"{\s*(?P<relation>[^()]+)\s+\(Score:\s+(?P<score>[0-9.]+)\)}"
    relations=[]
    for match in re.finditer(pattern, string):
        relation = match.group("relation").strip()
        relation = transform_relation(relation)
        if ';' in relation:
            continue
        score = match.group("score")
        if not relation or not score:
            return False, "output uncompleted.."
        try:
            score = float(score)
        except ValueError:
            return False, "Invalid score"
        if relation in head_relations:
            relations.append({"entity": entity_id, "relation": relation, "score": score, "head": True})
        else:
            relations.append({"entity": entity_id, "relation": relation, "score": score, "head": False})

    for dict in relations:
        for item in relationship:
            if dict['entity'] == item[0]:
                dict['relation'] = item[1]
                break
    if not relations:
        return False, "No relations found"
    return True, relations

def construct_relation_prune_prompt(question, entity_name, total_relations, args):
    return extract_relation_prompt_wiki % (args.width, args.width)+question+'\nTopic Entity: '+entity_name+ '\nRelations:\n'+'\n'.join([f"{i}. {item}" for i, item in enumerate(total_relations, start=1)])+'A:'


def check_end_word(s):
    words = [" ID", " code", " number", "instance of", "website", "URL", "inception", "image", " rate", " count"]
    return any(s.endswith(word) for word in words)


def abandon_rels(relation):
    useless_relation_list = ["category's main topic", "topic\'s main category", "stack exchange site", 'main subject', 'country of citizenship', "commons category", "commons gallery", "country of origin", "country", "nationality"]
    if check_end_word(relation) or 'wikidata' in relation.lower() or 'wikimedia' in relation.lower() or relation.lower() in useless_relation_list:
        return True
    return False


def construct_entity_score_prompt(question, relation, entity_candidates):
    print('q: ',question)
    print('r: ',relation)
    print('e: ',entity_candidates)
    return score_entity_candidates_prompt_wiki.format(question, relation) + "; ".join(entity_candidates) + '\nScore: '


def relation_search_prune(entity,  pre_relations, pre_head, question, args, graph):
    relations = []
    for graph_chunk in graph:
        node_found = None
        for node in graph_chunk['nodes']:
            if node['name'] == entity:
                node_found = node

        if node_found is None:
            continue

        temp = {}
        related = []

        for relationship in graph_chunk['relationships']:
            if relationship['source']['name'] == entity:
                relations.append(relationship['target']['name'] + relationship['properties']['triplet_sentence'])
                related.append((relationship['target']['name'], relationship['properties']['triplet_sentence']))
                temp[relationship['target']['name']] = relationship['properties']['triplet_sentence']

            if relationship['target']['name'] == entity:
                relations.append(relationship['source']['name'] + relationship['properties']['triplet_sentence'])
                related.append((relationship['source']['name'], relationship['properties']['triplet_sentence']))
                temp[relationship['source']['name']] = relationship['properties']['triplet_sentence']
    
    prompt = construct_relation_prune_prompt(question, entity, relations, args)

    # print(prompt)

    result = run_llm(prompt, args.temperature_exploration, args.max_length, args.opeani_api_keys, args.LLM_type)
    
    flag, retrieve_relations_with_scores = new_clean_relations(result, entity, relations, related) 
    # flag, retrieve_relations_with_scores = clean_relations(result, entity, relations) 


    for object in retrieve_relations_with_scores:
        if object['entity'] in temp:
            object['relation'] = temp[object['entity']]


    print('temp here: ', temp)

    print('retrieve_relations_with_scores: ', retrieve_relations_with_scores)

    print(result)
    # raise Exception("stop")

    if flag:
        return retrieve_relations_with_scores, temp
    else:
        return [] # format error or too small max_length
    

def del_all_unknown_entity(entity_candidates_id, entity_candidates_name):
    if len(entity_candidates_name) == 1 and entity_candidates_name[0] == "N/A":
        return entity_candidates_id, entity_candidates_name

    new_candidates_id = []
    new_candidates_name = []
    for i, candidate in enumerate(entity_candidates_name):
        if candidate != "N/A":
            new_candidates_id.append(entity_candidates_id[i])
            new_candidates_name.append(candidate)

    return new_candidates_id, new_candidates_name


def all_zero(topn_scores):
    return all(score == 0 for score in topn_scores)


def entity_search(entity, relation, graph, head):
    neighbors = []
    for graph_chunk in graph:
        node_found = None
        for node in graph_chunk['nodes']:
            if node['name'] == entity:
                node_found = node

        if node_found is None:
            continue

        for relationship in graph_chunk['relationships']:
            if relationship['source']['name'] == entity:
                neighbors.append(relationship['target']['name'])

            if relationship['target']['name'] == entity:
                neighbors.append(relationship['source']['name'])
    

    # id_list = [item['qid'] for item in entities_set]

    # print('neighbors: ', neighbors)
    
    return neighbors


def entity_score(question, entity_candidates, score, relation, args):
    if len(entity_candidates) == 1:
        return [score], entity_candidates
    if len(entity_candidates) == 0:
        return [0.0], entity_candidates
    
    # make sure the id and entity are in the same order
    # zipped_lists = sorted(zip(entity_candidates))
    # entity_candidates = zip(*zipped_lists)
    # entity_candidates = list(entity_candidates)

    prompt = construct_entity_score_prompt(question, relation, entity_candidates)

    result = run_llm(prompt, args.temperature_exploration, args.max_length, args.opeani_api_keys, args.LLM_type)
    entity_scores = clean_scores(result, entity_candidates)
    if all_zero(entity_scores):
        return [1/len(entity_candidates) * score] * len(entity_candidates), entity_candidates
    else:
        return [float(x) * score for x in entity_scores], entity_candidates


def update_history(entity_candidates, entity, scores, total_candidates, total_scores, total_relations, total_topic_entities, total_head, value_flag):
    if value_flag:
        scores = [1/len(entity_candidates) * entity['score']]
    candidates_relation = [entity['relation']] * len(entity_candidates)
    topic_entities = [entity['entity']] * len(entity_candidates)
    head_num = [entity['head']] * len(entity_candidates)
    total_candidates.extend(entity_candidates)
    total_scores.extend(scores)
    total_relations.extend(candidates_relation)
    total_topic_entities.extend(topic_entities)
    total_head.extend(head_num)
    return total_candidates, total_scores, total_relations, total_topic_entities, total_head


def half_stop(question, cluster_chain_of_entities, depth, args):
    print("No new knowledge added during search depth %d, stop searching." % depth)
    answer = generate_answer(question, cluster_chain_of_entities, args)
    save_2_jsonl(question, answer, cluster_chain_of_entities, file_name=args.dataset)


def generate_answer(question, cluster_chain_of_entities, args): 
    prompt = answer_prompt_wiki + question + '\n'
    chain_prompt = '\n'.join([', '.join([str(x) for x in chain]) for sublist in cluster_chain_of_entities for chain in sublist])
    prompt += "\nKnowledge Triplets: " + chain_prompt + 'A: '
    result = run_llm(prompt, args.temperature_reasoning, args.max_length, args.opeani_api_keys, args.LLM_type)
    return result


def entity_prune(total_relations, total_candidates, total_topic_entities, total_head, total_scores, args, wiki_client):
    zipped = list(zip( total_relations, total_candidates, total_topic_entities, total_head, total_scores))
    sorted_zipped = sorted(zipped, key=lambda x: x[4], reverse=True)
    sorted_relations, sorted_candidates, sorted_topic_entities, sorted_head, sorted_scores = [x[0] for x in sorted_zipped], [x[1] for x in sorted_zipped], [x[2] for x in sorted_zipped], [x[3] for x in sorted_zipped], [x[4] for x in sorted_zipped]

    relations, candidates, topics, heads, scores = sorted_relations[:args.width], sorted_candidates[:args.width], sorted_topic_entities[:args.width], sorted_head[:args.width], sorted_scores[:args.width]
    merged_list = list(zip(relations, candidates, topics, heads, scores))
    filtered_list = [(rel, ent, top, hea, score) for rel, ent, top, hea, score in merged_list if score != 0]
    if len(filtered_list) ==0:
        return False, [], [], [], []
    relations, candidates, tops, heads, scores = map(list, zip(*filtered_list))
    
    # tops = [wiki_client.query_all("qid2label", entity_id).pop() if (entity_name := wiki_client.query_all("qid2label", entity_id)) != "Not Found!" else "Unname_Entity" for entity_id in tops]
    # tops = 
    cluster_chain_of_entities = [[(relations[i], candidates[i]) for i in range(len(candidates))]]
    return True, cluster_chain_of_entities, relations, heads


def reasoning(question, cluster_chain_of_entities, args):
    prompt = prompt_evaluate_wiki + question
    chain_prompt = '\n'.join([', '.join([str(x) for x in chain]) for sublist in cluster_chain_of_entities for chain in sublist])
    prompt += "\nKnowledge Triplets: " + chain_prompt + 'A: '

    # print(chain_prompt)

    response = run_llm(prompt, args.temperature_reasoning, args.max_length, args.opeani_api_keys, args.LLM_type)

    # print('resopnse', response)
    
    result = extract_answer(response)
    if if_true(result):
        return True, response
    else:
        return False, response
    

def new_reasoning(question, cluster_chain_of_entities, args):
    prompt = prompt_evaluate_wiki + question
    
    # Generate the chain_prompt from the list of tuples
    chain_prompt = '\n'.join([f"{tup[0]}, {tup[1]}" for tup in cluster_chain_of_entities])
    
    prompt += "\nKnowledge Triplets: " + chain_prompt + 'A: '

    print("new reasoning: ",chain_prompt)

    # Call the LLM with the prompt
    response = run_llm(prompt, args.temperature_reasoning, args.max_length, args.opeani_api_keys, args.LLM_type)

    # Process the response and evaluate the result
    result = extract_answer(response)
    if if_true(result):
        return True, response
    else:
        return False, response
