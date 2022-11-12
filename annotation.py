import copy
import random
import string
from queue import Queue
from itertools import chain
import fuckit
try:
    from itertools import imap
except ImportError:
    # Python 3...
    imap=map
class Node(object):
    def __init__(self, node_type, relation_name, schema, alias, group_key, sort_key, join_type, index_name, 
            hash_cond, table_filter, index_cond, merge_cond, recheck_cond, join_filter, subplan_name, actual_rows,
            actual_time,description, total_cost):
        self.node_type = node_type
        self.children = []
        self.relation_name = relation_name
        self.schema = schema
        self.alias = alias
        self.group_key = group_key
        self.sort_key = sort_key
        self.join_type = join_type
        self.index_name = index_name
        self.hash_cond = hash_cond
        self.table_filter = table_filter
        self.index_cond = index_cond
        self.merge_cond = merge_cond
        self.recheck_cond = recheck_cond
        self.join_filter = join_filter
        self.subplan_name = subplan_name
        self.actual_rows = actual_rows
        self.actual_time = actual_time
        self.description = description
        self.total_cost = total_cost

    def add_children(self, child):
        self.children.append(child)
    
    def set_output_name(self, output_name):
        if "T" == output_name[0] and output_name[1:].isdigit():
            self.output_name = int(output_name[1:])
        else:
            self.output_name = output_name

    def get_output_name(self):
        if str(self.output_name).isdigit():
            return "T" + str(self.output_name)
        else:
            return self.output_name

    def set_step(self, step):
        self.step = step
    
    def update_desc(self,desc):
        self.description = desc
    
    def __iter__(self):
        for v in chain(*imap(iter, self.children)):
            yield v
        yield self
        
def parse_json(data):
    q = Queue()
    q_node = Queue()
    plan = data['Plan']
    q.put(plan)
    q_node.put(None)

    node_type_list = []
    node_total_cost = 0
    while not q.empty():
        current_plan = q.get()
        parent_node = q_node.get()

        relation_name = schema = alias = group_key = sort_key = join_type = index_name = hash_cond = table_filter \
            = index_cond = merge_cond = recheck_cond = join_filter = subplan_name = actual_rows = actual_time = description = None
        total_cost = 0
        if 'Relation Name' in current_plan:
            relation_name = current_plan['Relation Name']
        if 'Schema' in current_plan:
            schema = current_plan['Schema']
        if 'Alias' in current_plan:
            alias = current_plan['Alias']
        if 'Group Key' in current_plan:
            group_key = current_plan['Group Key']
        if 'Sort Key' in current_plan:
            sort_key = current_plan['Sort Key']
        if 'Join Type' in current_plan:
            join_type = current_plan['Join Type']
        if 'Index Name' in current_plan:
            index_name = current_plan['Index Name']
        if 'Hash Cond' in current_plan:
            hash_cond = current_plan['Hash Cond']
        if 'Filter' in current_plan:
            table_filter = current_plan['Filter']
        if 'Index Cond' in current_plan:
            index_cond = current_plan['Index Cond']
        if 'Merge Cond' in current_plan:
            merge_cond = current_plan['Merge Cond']
        if 'Recheck Cond' in current_plan:
            recheck_cond = current_plan['Recheck Cond']
        if 'Join Filter' in current_plan:
            join_filter = current_plan['Join Filter']
        if 'Actual Rows' in current_plan:
            actual_rows = current_plan['Actual Rows']
        if 'Actual Total Time' in current_plan:
            actual_time = current_plan['Actual Total Time']
        if 'Subplan Name' in current_plan:
            if "returns" in current_plan['Subplan Name']:
                name = current_plan['Subplan Name']
                subplan_name = name[name.index("$"):-1]
            else:
                subplan_name = current_plan['Subplan Name']
        if 'Total Cost' in current_plan:
            total_cost = current_plan['Total Cost']
        current_node = Node(current_plan['Node Type'], relation_name, schema, alias, group_key, sort_key, join_type,
                            index_name, hash_cond, table_filter, index_cond, merge_cond, recheck_cond, join_filter,
                            subplan_name, actual_rows, actual_time, description, total_cost)
        node_type_list.append(current_node.node_type)
        node_total_cost += current_node.total_cost
        # print("hash cond ", current_node.hash_cond)
        # print("index cond ", current_node.index_cond)
        # print("merge cond ", current_node.merge_cond)
        if "Limit" == current_node.node_type:
            current_node.plan_rows = current_plan['Plan Rows']

        if "Scan" in current_node.node_type:
            if "Index" in current_node.node_type:
                if relation_name:
                    current_node.set_output_name(
                        relation_name + " with index " + index_name)
            elif "Subquery" in current_node.node_type:
                current_node.set_output_name(alias)
            else:
                current_node.set_output_name(relation_name)

        if parent_node is not None:
            parent_node.add_children(current_node)
        else:
            head_node = current_node

        if 'Plans' in current_plan:
            for item in current_plan['Plans']:
                # push child plans into queue
                q.put(item)
                # push parent for each child into queue
                q_node.put(current_node)

    return head_node, node_type_list, int(node_total_cost)

def simplify_graph(node):
    new_node = copy.deepcopy(node)
    new_node.children = []

    for child in node.children:
        new_child = simplify_graph(child)
        new_node.add_children(new_child)
        new_node.actual_time -= child.actual_time

    if node.node_type in ["Result"]:
        return node.children[0]

    return new_node


def parse_cond(op_name, conditions, table_subquery_name_pair):
    if isinstance(conditions,str):
        if "::" in conditions:
            return conditions.replace("::", " ")[1:-1]
        return conditions[1:-1]
    cond = ""
    for i in range (len(conditions)):
        cond = cond + conditions[i]
        if (not (i == len(conditions)-1)):
            cond = cond + "and"
    return cond


def to_text(node, skip=False):
    global steps, cur_step, cur_table_name
    increment = True
    # skip the child if merge it with current node
    if node.node_type in ["Unique", "Aggregate"] and len(node.children) == 1 \
            and ("Scan" in node.children[0].node_type or node.children[0].node_type == "Sort"):
        children_skip = True
    elif node.node_type == "Bitmap Heap Scan" and node.children[0].node_type == "Bitmap Index Scan":
        children_skip = True
    else:
        children_skip = False

    # recursive
    for child in node.children:
        if node.node_type == "Aggregate" and len(node.children) > 1 and child.node_type == "Sort":
            to_text(child, True)
        else:
            to_text(child, children_skip)

    if node.node_type in ["Hash"] or skip:
        return

    step = ""

    # generate natural language for various QEP operators
    if "Join" in node.node_type:
        # special preprocessing for joins
        if node.join_type == "Semi":
            # add the word "Semi" before "Join" into node.node_type
            node_type_list = node.node_type.split()
            node_type_list.insert(-1, node.join_type)
            node.node_type = " ".join(node_type_list)
        else:
            pass

        if "Hash" in node.node_type:
            step += " and perform " + node.node_type.lower() + " on "
            for i, child in enumerate(node.children):
                if child.node_type == "Hash":
                    child.set_output_name(child.children[0].get_output_name())
                    hashed_table = child.get_output_name()
                if i < len(node.children) - 1:
                    step += (" table " + child.get_output_name())
                else:
                    step += (" and table " + child.get_output_name())
            # combine hash with hash join
            step = "hash table " + hashed_table + step + " under condition " + \
                parse_cond("Hash Con ", node.hash_cond,
                           table_subquery_name_pair)

        elif "Merge" in node.node_type:
            step += "perform " + node.node_type.lower() + " on "
            any_sort = False  # whether sort is performed on any table
            for i, child in enumerate(node.children):
                if child.node_type == "Sort":
                    child.set_output_name(child.children[0].get_output_name())
                    any_sort = True
                if i < len(node.children) - 1:
                    step += ("table " + child.get_output_name())
                else:
                    step += (" and table " + child.get_output_name())
            # combine sort with merge join
            if any_sort:
                sort_step = "sort "
                for child in node.children:
                    if child.node_type == "Sort":
                        if i < len(node.children) - 1:
                            sort_step += ("table " + child.get_output_name())
                        else:
                            sort_step += (" and table " +
                                          child.get_output_name())
                step = sort_step + " and " + step

    elif node.node_type == "Bitmap Heap Scan":
        # combine bitmap heap scan and bitmap index scan
        if "Bitmap Index Scan" in node.children[0].node_type:
            node.children[0].set_output_name(node.relation_name)
            step = " with index condition " + \
                parse_cond("Recheck Cond", node.recheck_cond,
                           table_subquery_name_pair)

        step = "perform bitmap heap scan on table " + \
            node.children[0].get_output_name() + step

    elif "Scan" in node.node_type:
        if node.node_type == "Seq Scan":
            step += "perform sequential scan on table "
        else:
            step += "perform " + node.node_type.lower() + " on table "

        step += node.get_output_name()

        # if no table filter, remain original table name
        if not node.table_filter:
            increment = False

    elif node.node_type == "Unique":
        # combine unique and sort
        if "Sort" in node.children[0].node_type:
            node.children[0].set_output_name(
                node.children[0].children[0].get_output_name())
            step = "sort " + node.children[0].get_output_name()
            if node.children[0].sort_key:
                step += " with attribute " + \
                    parse_cond(
                        "Sort Key", node.children[0].sort_key, table_subquery_name_pair) + " and "

            else:
                step += " and "

        step += "perform unique on table " + node.children[0].get_output_name()

    elif node.node_type == "Aggregate":
        for child in node.children:
            # combine aggregate and sort
            if "Sort" in child.node_type:
                child.set_output_name(child.children[0].get_output_name())
                step = "sort " + child.get_output_name() + " and "
            # combine aggregate with scan
            if "Scan" in child.node_type:
                if child.node_type == "Seq Scan":
                    step = "perform sequential scan on " + child.get_output_name() + " and "
                else:
                    step = "perform " + child.node_type.lower() + " on " + \
                        child.get_output_name() + " and "

        step += "perform aggregate on table " + \
            node.children[0].get_output_name()
        if len(node.children) == 2:
            step += " and table " + node.children[1].get_output_name()

    elif node.node_type == "Sort":
        step += "perform sort on table " + node.children[0].get_output_name(
        ) + " with attribute " + parse_cond("Sort Key", node.sort_key, table_subquery_name_pair)

    elif node.node_type == "Limit":
        step += "limit the result from table " + \
            node.children[0].get_output_name() + " to " + \
            str(node.plan_rows) + " record(s)"

    else:
        step += "perform " + node.node_type.lower() + " on"
        # binary operator
        if len(node.children) > 1:
            for i, child in enumerate(node.children):
                if i < len(node.children) - 1:
                    step += (" table " + child.get_output_name() + ",")
                else:
                    step += (" and table " + child.get_output_name())
        # unary operator
        else:
            step += " table " + node.children[0].get_output_name()
    if node.total_cost:
            step += " with cost " + str(node.total_cost)
    # add conditions
    if node.group_key:
        step += " with grouping on attribute " + \
            parse_cond("Group Key", node.group_key, table_subquery_name_pair)

    if node.table_filter:
        step += " and filtering on " + \
            parse_cond("Table Filter", node.table_filter,
                       table_subquery_name_pair)

    if node.join_filter:
        step += " while filtering on " + \
            parse_cond("Join Filter", node.join_filter,
                       table_subquery_name_pair)

    # set intermediate table name
    if increment:
        node.set_output_name("T" + str(cur_table_name))
        step += " to get intermediate table " + node.get_output_name()
        cur_table_name += 1
    if node.subplan_name:
        table_subquery_name_pair[node.subplan_name] = node.get_output_name()

    
    node.update_desc(step)
    step = "Step " + str(cur_step) + ". " + step + "."
    node.set_step(cur_step)
    cur_step += 1

    steps.append(step)


def random_word(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))


def get_text(json_obj):
    global steps, cur_step, cur_table_name, table_subquery_name_pair
    global current_plan_tree
    steps = ["The query is executed as follow."]
    cur_step = 1
    cur_table_name = 1
    table_subquery_name_pair = {}

    head_node = parse_json(json_obj)[0]
    simplified_graph = simplify_graph(head_node)

    to_text(simplified_graph)
    if " to get intermediate table" in steps[-1]:
        steps[-1] = steps[-1][:steps[-1].index(
            " to get intermediate table")] + ' to get the final result.'

    return steps

def clear_cache():
    global steps, cur_step, cur_table_name, table_subquery_name_pair
    steps = []
    cur_step = 1
    cur_table_name = 1
    table_subquery_name_pair = {}

def generate_tree(tree, node, _prefix="", _last=True):
    if _last:
        tree = "{}`-- {}\n".format(_prefix, node.node_type)
    else:
        tree = "{}|-- {}\n".format(_prefix, node.node_type)

    _prefix += "   " if _last else "|  "
    child_count = len(node.children)
    for i, child in enumerate(node.children):
        _last = i == (child_count - 1)
        tree = tree + generate_tree(tree, child, _prefix, _last)
    return tree


def generate_why(node_a, node_b, num):

    text = ""
    if node_a.node_type =="Index Scan" and node_b.node_type == "Seq Scan":
        text = "Reason for Difference " + str(num) + ": " 
        text += node_a.node_type + " in P1 on relation " + node_a.relation_name + " has now evolved to Sequential Scan in P2 on relation " + node_b.relation_name + ". This is because "
        if node_b.index_name is None:
            text += "P1 uses the index, i.e. " + node_a.index_name + ", for selection while P2 doesn't. "
        if int(node_a.actual_rows) < int(node_b.actual_rows):
            text += "and the actual row number increases from " + str(node_a.actual_rows) + " to " + str(node_b.actual_rows) + ", "

        if node_a.index_cond != node_b.table_filter and int(node_a.actual_rows) < int(node_b.actual_rows):
            text += "This may be due to the selection predicates change from " + (node_a.index_cond if node_a.index_cond is not None else "None ") + " to " + (node_b.table_filter if node_b.table_filter is not None else "None ") + ". "
        if node_a.total_cost < node_b.total_cost:
            text += "and the cost increases from " + str(node_a.total_cost) + " to " + str(node_b.total_cost) + ". "

    elif node_b.node_type =="Index Scan" and node_a.node_type == "Seq Scan":
        text = "Reason for Difference " + str(num) + ": " 
        text += "Sequential Scan in P1 on relation " + node_a.relation_name + " has now evolved to " + node_b.node_type +" in P2 on relation " + node_b.relation_name + ". This is because "
        if  node_a.index_name is None:  
            text += "P2 uses the index, i.e. " + node_b.index_name + ", for selection while P1 doesn't. "
        elif node_a.index_name is not None:
            text += "Both P1 and P2 uses the index, which are respectively " + node_a.index_name + " and " + node_b.index_name + ". "
        if int(node_a.actual_rows) > int(node_b.actual_rows):
            text += "and the actual row number decreases from " + str(node_a.actual_rows) + " to " + str(node_b.actual_rows) + ". "
        if node_a.table_filter != node_b.index_cond and int(node_a.actual_rows) > int(node_b.actual_rows):
            text += "This may be due to the selection predicate changes from " + (node_a.table_filter if node_a.table_filter is not None else "None") + " to " + (node_b.index_cond if node_b.index_cond is not None else "None") + ". "
        if node_a.total_cost < node_b.total_cost:
            text += "and the cost increases from " + str(node_a.total_cost) + " to " + str(node_b.total_cost) + ". "
    elif node_a.node_type and node_b.node_type in ['Merge Join', "Hash Join", "Nested Loop"]:
        text = "Reason for Difference " + str(num) + ": " 
        if node_a.node_type == "Nested Loop" and node_b.node_type == "Merge Join":
            text += node_a.node_type + " in P1 on has now evolved to " + node_b.node_type +" in P2 on relation " + ". This is because "
            if int(node_a.actual_rows) < int(node_b.actual_rows):
                text += "the actual row number increases from " + str(node_a.actual_rows) + " to " + str(node_b.actual_rows) + ", "
            if "=" in node_b.node_type:
                text += "The join condition uses an equality operator. "
            if node_a.total_cost < node_b.total_cost:
                text += "and the cost increases from " + str(node_a.total_cost) + " to " + str(node_b.total_cost) + ". "
            text += "The both side of the Join operator of P2 can be sorted on the join condition efficiently . "

        if node_a.node_type == "Nested Loop" and node_b.node_type == "Hash Join":
            text += node_a.node_type + " in P1 on has now evolved to " + node_b.node_type +" in P2 on relation " + ". This is because "
            if int(node_a.actual_rows) < int(node_b.actual_rows):
                text += "the actual row number increases from " + str(node_a.actual_rows) + " to " + str(node_b.actual_rows) + ". "
            if "=" in node_b.node_type:
                text += "The join condition uses an equality operator. "
            if node_a.total_cost < node_b.total_cost:
                text += "and the cost increases from " + str(node_a.total_cost) + " to " + str(node_b.total_cost) + ". "
        if node_a.node_type == "Merge Join" and node_b.node_type == "Nested Loop":
            text += node_a.node_type + " in P1 on has now evolved to " + node_b.node_type +" in P2 on relation " + ". This is because "
            if int(node_a.actual_rows) > int(node_b.actual_rows):
                text += "the actual row number decreases from " + str(node_a.actual_rows) + " to " + str(node_b.actual_rows) + ". "
            elif int(node_a.actual_rows) < int(node_b.actual_rows):
                text += "the actual row number increases from " + str(node_a.actual_rows) + " to " + str(node_b.actual_rows) + ". "
                text += node_b.node_type + " joins are used  if the join condition does not use the equality operator"
            if node_a.total_cost < node_b.total_cost:
                text += "and the cost increases from " + str(node_a.total_cost) + " to " + str(node_b.total_cost) + ". "
            
        if node_a.node_type == "Merge Join" and node_b.node_type == "Hash Join":
            text += node_a.node_type + " in P1 on has now evolved to " + node_b.node_type +" in P2 on relation " + ". " 
            if int(node_a.actual_rows) < int(node_b.actual_rows):
                text += "This is because the actual row number increases from " + str(node_a.actual_rows) + " to " + str(node_b.actual_rows) + ". "
            if int(node_a.actual_rows) > int(node_b.actual_rows):
                text += "The actual row number decreases from " + str(node_a.actual_rows) + " to " + str(node_b.actual_rows) + ". "
            if node_a.total_cost < node_b.total_cost:
                text += "and the cost increases from " + str(node_a.total_cost) + " to " + str(node_b.total_cost) + ". "
            text += "The both side of the Join operator of P2 can be sorted on the join condition efficiently . "

        if node_a.node_type == "Hash Join" and node_b.node_type == "Nested Loop":
            text += node_a.node_type + " in P1 on has now evolved to " + node_b.node_type +" in P2 on relation " + ". This is because "
            if int(node_a.actual_rows) > int(node_b.actual_rows):
                text += "the actual row number decreases from " + str(node_a.actual_rows) + " to " + str(node_b.actual_rows) + ". "
            elif int(node_a.actual_rows) < int(node_b.actual_rows):
                text += "the actual row number increases from " + str(node_a.actual_rows) + " to " + str(node_b.actual_rows) + ". "
                text += node_b.node_type + " joins are used  if the join condition does not use the equality operator"
            if node_a.total_cost < node_b.total_cost:
                text += "and the cost increases from " + str(node_a.total_cost) + " to " + str(node_b.total_cost) + ". "

        if node_a.node_type == "Hash Join" and node_b.node_type == "Merge Join":
            text += node_a.node_type + " in P1 on has now evolved to " + node_b.node_type +" in P2 on relation " + ". " 
            if int(node_a.actual_rows) < int(node_b.actual_rows):
                text += "The actual row number increases from " + str(node_a.actual_rows) + " to " + str(node_b.actual_rows) + ". "
            if int(node_a.actual_rows) > int(node_b.actual_rows):
                text += "The actual row number decreases from " + str(node_a.actual_rows) + " to " + str(node_b.actual_rows) + ". "
            if node_a.total_cost < node_b.total_cost:
                text += "and the cost increases from " + str(node_a.total_cost) + " to " + str(node_b.total_cost) + ". "
            text += "The both side of the Join operator of P2 can be sorted on the join condition efficiently. "

    return text


def modify_text(str):
    str = str.replace('perform ', '')
    return str

def check_children(nodeA, nodeB, difference, reasons):
    global num
    childrenA = nodeA.children
    childrenB = nodeB.children
    children_no_A = len(childrenA)
    children_no_B = len(childrenB)

    if nodeA.node_type == nodeB.node_type and children_no_A == children_no_B:
        if children_no_A != 0:
            for i in range(len(childrenA)):
                check_children(childrenA[i], childrenB[i],  difference, reasons)

    else:
        if nodeA.node_type == 'Hash' or nodeA.node_type == 'Sort':
            text = 'Reason ' + \
                str(num) + ' : ' + nodeA.children[0].description + \
                ' as compared to AEP with ' + nodeB.description
            text = modify_text(text)
            difference.append(text)
            reason = generate_why(nodeA.children[0], nodeB, num)
            reasons.append(reason)
            num += 1

        elif nodeB.node_type == 'Hash' or nodeB.node_type == 'Sort':
            text = 'Reason ' + str(num) + ' : ' + nodeA.description + \
                ' as compared to AEP with ' + nodeB.children[0].description
            text = modify_text(text)
            difference.append(text)
            reason = generate_why(nodeA, nodeB.children[0], num)
            reasons.append(reason)
            num += 1

        elif nodeA.node_type == 'Hash Join' or nodeA.node_type == 'Merge Join' or nodeA.node_type == 'Nested Loop':
            text = 'Reason ' + str(num) + ' : ' + nodeA.children[0].description + \
                ' as compared to AEP with ' + nodeB.children[0].description
            text = modify_text(text)
            difference.append(text)
            reason = generate_why(nodeA.children[0], nodeB.children[0], num)
            reasons.append(reason)
            num += 1
        
        elif nodeB.node_type == 'Hash Join' or nodeB.node_type == 'Merge Join' or nodeB.node_type == 'Nested Loop':
            text = 'Reason ' + str(num) + ' : ' + nodeA.description + \
                ' as compared to AEP with ' + nodeB.children[0].description
            text = modify_text(text)
            difference.append(text)
            reason = generate_why(nodeA, nodeB.children[0], num)
            reasons.append(reason)
            num += 1
        
        elif nodeA.node_type == 'Seq Scan' or nodeA.node_type == 'Index Scan' or nodeA.node_type == 'Bitmap Heap Scan':
            text = 'Reason ' + str(num) + ' : ' + nodeA.description + \
                ' as compared to AEP with ' + nodeB.description
            text = modify_text(text)
            difference.append(text)
            reason = generate_why(nodeA, nodeB, num)
            reasons.append(reason)
            num += 1
        
        elif nodeB.node_type == 'Seq Scan' or nodeB.node_type == 'Index Scan' or nodeB.node_type == 'Bitmap Heap Scan':
            try:
                text = 'Reason ' + str(num) + ' : ' + nodeA.description + \
                    ' as compared to AEP with ' + nodeB.description
                text = modify_text(text)
                difference.append(text)
                reason = generate_why(nodeA, nodeB, num)
                reasons.append(reason)
                num += 1
            except:
                pass
        elif 'Gather' in nodeA.node_type:
            check_children(childrenA[0], nodeB, difference, reasons)

        elif 'Gather' in nodeB.node_type:
            check_children(nodeA, childrenB[0],  difference, reasons)
        else:
            try:
                text = 'Reason ' + \
                    str(num) + ' : ' + nodeA.description + \
                    ' as compared to AEP with ' + nodeB.description
                text = modify_text(text)
                difference.append(text)
                reason = generate_why(nodeA, nodeB, num)
                reasons.append(reason)
            except:
                pass
            num += 1

        if children_no_A == children_no_B:
            if children_no_A == 1:
                check_children(childrenA[0], childrenB[0], difference, reasons)
            if children_no_A == 2:
                check_children(childrenA[0], childrenB[0], difference, reasons)
                check_children(childrenA[1], childrenB[1],  difference, reasons)

def generate_why_cost(QEP, AQP, QEP_cost, AQP_cost):
    global text 
    text = ""
    
    if QEP.node_type in ['Seq Scan', 'Index Scan', 'Bitmap Heap Scan']:
        if QEP.total_cost < AQP.total_cost:
            text += "Reason: " + QEP.relation_name + " is read using " + QEP.node_type + " because the cost of " + QEP.node_type + "\n"\
                    " , which is " + str(QEP.total_cost) + " is lower than the cost of " + AQP.node_type + "\n"\
                    " , which is " + str(AQP.total_cost) + ". "
        elif QEP.total_cost == AQP.total_cost:
            text += "Reason: Although the cost of reading " + QEP.relation_name + " using " + QEP.node_type + "\n"\
                    " ," + str(QEP.total_cost) + ", is equal to the cost of reading " + QEP.relation_name + " using " + AQP.node_type + "\n"\
                    " which is " + str(AQP.total_cost) + ", the total cost of the QEP is " + str(QEP_cost) + "\n"\
                    " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
        else:
            text += "Reason: Although the cost of reading " + QEP.relation_name + " using " + QEP.node_type + "\n"\
                    " ," + str(QEP.total_cost) + ", is higher than the cost of reading " + QEP.relation_name + " using " + AQP.node_type + "\n"\
                    " which is " + str(AQP.total_cost) + ", the total cost of the QEP is " + str(QEP_cost) + "\n"\
                    " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
    
    elif QEP.node_type in ['Hash Join', 'Merge Join', 'Nested Loop']:
        if QEP.total_cost < AQP.total_cost:
            if QEP.hash_cond:
                if AQP.hash_cond or AQP.merge_cond:
                    text += "Reason: This join is implemented using " + QEP.node_type + " because the cost of "+ QEP.node_type + "\n"\
                            " joining " + QEP.hash_cond + " is " + str(QEP.total_cost) + \
                            " which is lower than the cost of using " + AQP.node_type + " which is " + str(AQP.total_cost) + ". "
                else:
                    text += "Reason: This join is implemented using " + QEP.node_type + " because the cost of "+ QEP.node_type + "\n"\
                            " joining " + QEP.hash_cond + " is " + str(QEP.total_cost) + \
                            " which is lower than the cost of using Nested Loop which is " + str(AQP.total_cost) + ". "
            elif QEP.merge_cond:
                if AQP.hash_cond or AQP.merge_cond:
                    text += "Reason: This join is implemented using " + QEP.node_type + " because the cost of "+ QEP.node_type + "\n"\
                            " joining " + QEP.merge_cond + " is " + str(QEP.total_cost) \
                            + " which is lower than the cost of using " + AQP.node_type + " which is " + str(AQP.total_cost) + ". "
                else:
                    text += "Reason: This join is implemented using " + QEP.node_type + " because the cost of "+ QEP.node_type + "\n"\
                            " joining " + QEP.merge_cond + " is " + str(QEP.total_cost) + \
                            " which is lower than the cost " + " of using Nested Loop which is " + str(AQP.total_cost) + ". "
            else:
               text += "Reason: This join is implemented using " + QEP.node_type + " because the cost of "+ QEP.node_type + "\n"\
                       " joining is " + str(QEP.total_cost) + " which is lower than the cost " + " of using " + AQP.node_type + "\n"\
                        " which is " + str(AQP.total_cost) + ". "
    
        elif QEP.total_cost == AQP.total_cost:
            if QEP.hash_cond:
                if AQP.hash_cond or AQP.merge_cond:
                    text += "Reason: The cost of "+ QEP.node_type + " joining " + QEP.hash_cond + " , " + str(QEP.total_cost) + "\n"\
                            ", is same as " + AQP.node_type + " , with cost " + str(AQP.total_cost) + ". " + "\n"\
                            "However, the total cost of the QEP is " + str(QEP_cost) + "\n"\
                            " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
                else:
                    text += "Reason: The cost of "+ QEP.node_type + " joining " + QEP.hash_cond + " , " + str(QEP.total_cost) + "\n"\
                            ", is same as "+ AQP.node_type + " , with cost " + str(AQP.total_cost) + "\n"\
                            ", followed by Memoize and Nested Loop. " + "\n"\
                            "However, the total cost of the QEP is " + str(QEP_cost) + "\n"\
                            " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
            
            elif QEP.merge_cond:
                if AQP.hash_cond or AQP.merge_cond:
                    text += "Reason: The cost of "+ QEP.node_type + " joining " + QEP.merge_cond + " , " + str(QEP.total_cost) + "\n"\
                            ", is same as " + AQP.node_type + " , with cost " + str(AQP.total_cost) + ". " + "\n"\
                            "However, the total cost of the QEP is " + str(QEP_cost) + "\n"\
                            " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
                else:
                    text += "Reason: The cost of "+ QEP.node_type + " joining " + QEP.hash_cond + " , " + str(QEP.total_cost) + "\n"\
                            ", is same as "+ AQP.node_type + " , with cost " + str(AQP.total_cost) + "\n"\
                            ", followed by Memoize and Nested Loop. " + "\n"\
                            "However, the total cost of the QEP is " + str(QEP_cost) + "\n"\
                            " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
            else:
                text += "Reason: The cost of "+ QEP.node_type + " , " + str(QEP.total_cost) + "\n"\
                        ", is same as " + AQP.node_type + " , with cost " + str(AQP.total_cost) + ". " + "\n"\
                        "However, the total cost of the QEP is " + str(QEP_cost) + "\n"\
                        " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
    
        else:
            if QEP.hash_cond:
                if AQP.hash_cond or AQP.merge_cond:
                    text += "Reason: Although the cost of joining " + QEP.hash_cond + " using " + QEP.node_type + "\n"\
                            " ," + str(QEP.total_cost) + ", is higher than the cost of joining " + QEP.hash_cond + "\n"\
                            " using " + AQP.node_type + " with cost " + str(AQP.total_cost) + "\n"\
                            ", the total cost of the QEP is " + str(QEP_cost) + "\n"\
                            " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
                else:
                    text += "Reason: Although the cost of joining " + QEP.hash_cond + " using " + QEP.node_type + "\n"\
                            " ," + str(QEP.total_cost) + ", is higher than the cost of joining"+ \
                            " using " + AQP.node_type + " with cost " + str(AQP.total_cost) + "\n"\
                            " followed by Memoize and Nested Loop, \n the total cost of the QEP is " + str(QEP_cost) + \
                            " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
            elif QEP.merge_cond:
                if AQP.hash_cond or AQP.merge_cond:
                    text += "Reason: Although the cost of joining " + QEP.merge_cond + " using " + QEP.node_type + "\n"\
                            " ," + str(QEP.total_cost) + ", is higher than the cost of joining " + QEP.merge_cond + "\n"\
                            " using " + AQP.node_type + " with cost " + str(AQP.total_cost) + "\n"\
                            ", the total cost of the QEP is " + str(QEP_cost) + "\n"\
                            " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
                else:
                    text += "Reason: Although the cost of joining " + QEP.merge_cond + " using " + QEP.node_type + "\n"\
                            " ," + str(QEP.total_cost) + ", is higher than the cost of joining" + "\n"\
                            " using " + AQP.node_type + \
                            " followed by Memoize and Nested Loop, \nthe total cost of the QEP is " + str(QEP_cost) + \
                            " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
            else:
                text += "Reason: Although the cost of joining using " + QEP.node_type + " ," + str(QEP.total_cost) + "\n"\
                        " ,is higher than the cost of joining using " + AQP.node_type + "\n"\
                        " which is " + str(AQP.total_cost) + ", the total cost of the QEP is " + str(QEP_cost) + "\n"\
                        " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
    
    elif QEP.node_type in ['Gather, Aggregate']:
        return text

    elif QEP.node_type in ['Sort', 'Incremental Sort']:
        print('in sort')
        for i in range(len(QEP.sort_key)):
            if '::' in (QEP.sort_key)[i]:
                (QEP.sort_key).remove((QEP.sort_key)[i])
                break

        print(QEP.sort_key)
        if QEP.total_cost < AQP.total_cost:
            text += "Reason: This sort is implemented using " + QEP.node_type + " because the cost of "+ QEP.node_type + "\n"\
                    " sorting " + ''.join(QEP.sort_key) + " is " + str(QEP.total_cost) + "\n"\
                    " which is less than the cost " + " of using " + AQP.node_type + \
                    " which is " + str(AQP.total_cost) + ". "
        elif QEP.total_cost == AQP.total_cost:
            text += "Reason: The cost of "+ QEP.node_type + " sorting " + QEP.sort_key + " , " + str(QEP.total_cost) + "\n"\
                    " ,is same as " + AQP.node_type + " , with cost " + str(AQP.total_cost) + ". " + "\n"\
                    "However, the total cost of the QEP is " + str(QEP_cost) + "\n"\
                        " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
        else:
           text += "Reason: The cost of "+ QEP.node_type + " , " + str(QEP.total_cost) + "\n"\
                    ", is higher than " + AQP.node_type + " , with cost " + str(AQP.total_cost) + ". " + "\n"\
                    "However, the total cost of the QEP is " + str(QEP_cost) + "\n"\
                    " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
    
    
    else:
        if QEP.total_cost < AQP.total_cost:
            if QEP.relation_name:
                text += "Reason: The cost of " + QEP.node_type + " on " + QEP.relation_name + " is " + str(QEP.total_cost) + "\n"\
                        " which is lower than the cost of using " + AQP.node_type + " which is " + str(AQP.total_cost) + ". "
            else:
                text += "Reason: The cost of " + QEP.node_type + " is " + str(QEP.total_cost) + "\n"\
                        " which is lower than the cost of using " + AQP.node_type + " which is " + str(AQP.total_cost) + ". "

        elif QEP.total_cost == AQP.total_cost:
            if QEP.relation_name:
                text += "Reason: The cost of " + QEP.node_type + " on " + QEP.relation_name + " is " + str(QEP.total_cost) + "\n"\
                        " which is same as the cost of using " + AQP.node_type + " which is " + str(AQP.total_cost) + ". " + "\n" \
                        "However, the total cost of the QEP is " + str(QEP_cost) + " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
            else:
                text += "Reason: The cost of " + QEP.node_type + " is " + str(QEP.total_cost) + "\n"\
                        " which is same as the cost of using " + AQP.node_type + " which is " + str(AQP.total_cost) + ". " + "\n"\
                        "However, the total cost of the QEP is " + str(QEP_cost) + " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
        else:
            if QEP.relation_name:
                text += "Reason: The cost of " + QEP.node_type + " on " + QEP.relation_name + " is " + str(QEP.total_cost) + "\n"\
                        " which is higher than the cost of using " + AQP.node_type + " which is " + str(AQP.total_cost) + ". " + "\n"\
                        "However, the total cost of the QEP is " + str(QEP_cost) + " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
            else:
                text += "Reason: The cost of " + QEP.node_type + " is " + str(QEP.total_cost) + "\n"\
                        " which is higher than the cost of using " + AQP.node_type + " which is " + str(AQP.total_cost) + ". " + "\n"\
                        "However, the total cost of the QEP is " + str(QEP_cost) + " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "

    return text

def check_why_children(QEP, AQP, reasons, QEP_nodes, QEP_cost, AQP_cost):
    # QEP_children = QEP.children
    # AQP_children = AQP.children
    # QEP_children_no = len(QEP_children)
    # AQP_children_no = len(AQP_children)
    # print(QEP.node_type, AQP.node_type)
    # print(QEP.relation_name, AQP.relation_name)
    # print(QEP.hash_cond, AQP.hash_cond)
    # print(QEP.merge_cond, AQP.merge_cond)

    QEP_children_list = list(iter(QEP))
    AQP_children_list = list(iter(AQP))
    for children in QEP_children_list:
        print("QEP",children.node_type, children.relation_name, children.hash_cond, children.merge_cond, children.join_filter)
    
    for children in AQP_children_list:
        print("AQP ",children.node_type, children.relation_name, children.hash_cond, children.merge_cond, children.join_filter, children.recheck_cond)
    for qep_children in QEP_children_list:
        #print(qep_children.node_type, qep_children.relation_name, qep_children.hash_cond, qep_children.merge_cond)
        for aqp_children in AQP_children_list:
            #print(aqp_children.node_type, aqp_children.relation_name, aqp_children.hash_cond, aqp_children.merge_cond, aqp_children.join_filter)
            if qep_children.node_type in ['Seq Scan', 'Bitmap Heap Scan', 'Bitmap Index Scan', 'CTE Scan']:
                if qep_children.relation_name == aqp_children.relation_name or qep_children.relation_name == aqp_children.index_name:
                    print("In Scan")
                    print("QEP",qep_children.node_type, qep_children.relation_name, qep_children.hash_cond, qep_children.merge_cond)
                    print("AQP ",aqp_children.node_type, aqp_children.relation_name, aqp_children.hash_cond, aqp_children.merge_cond, aqp_children.join_filter)
                    reason = generate_why_cost(qep_children, aqp_children, QEP_cost, AQP_cost)
                    reasons.append(reason)
                    QEP_nodes.append(qep_children)
                    break
            
            if qep_children.node_type == 'Index Scan':
                if qep_children.index_name == aqp_children.index_name or qep_children.index_name == aqp_children.relation_name:
                    reason = generate_why_cost(qep_children, aqp_children, QEP_cost, AQP_cost)
                    reasons.append(reason)
                    QEP_nodes.append(qep_children)
                    break
            if qep_children.node_type == 'Hash Join':
                join_cond = ''.join(sorted(qep_children.hash_cond))
                print(join_cond)
                if aqp_children.recheck_cond:
                    if join_cond == aqp_children.hash_cond or join_cond == ''.join(sorted(aqp_children.recheck_cond)):
                        print("In Hash Join")
                        print("QEP",qep_children.node_type, qep_children.relation_name, qep_children.hash_cond, qep_children.merge_cond)
                        print("AQP ",aqp_children.node_type, aqp_children.relation_name, aqp_children.hash_cond, aqp_children.merge_cond, aqp_children.join_filter, aqp_children.recheck_cond)
                        reason = generate_why_cost(qep_children, aqp_children, QEP_cost, AQP_cost)
                        reasons.append(reason)
                        QEP_nodes.append(qep_children)
                        break
                elif aqp_children.merge_cond:
                    if join_cond == aqp_children.hash_cond or join_cond == ''.join(sorted(aqp_children.merge_cond)):
                        print("In Hash Join")
                        print("QEP",qep_children.node_type, qep_children.relation_name, qep_children.hash_cond, qep_children.merge_cond)
                        print("AQP ",aqp_children.node_type, aqp_children.relation_name, aqp_children.hash_cond, aqp_children.merge_cond, aqp_children.join_filter, aqp_children.recheck_cond)
                        reason = generate_why_cost(qep_children, aqp_children, QEP_cost, AQP_cost)
                        reasons.append(reason)
                        QEP_nodes.append(qep_children)
                        break
                elif aqp_children.join_filter:
                    if join_cond == aqp_children.hash_cond or join_cond == ''.join(sorted(aqp_children.join_filter)):
                        print("In Hash Join")
                        print("QEP",qep_children.node_type, qep_children.relation_name, qep_children.hash_cond, qep_children.merge_cond)
                        print("AQP ",aqp_children.node_type, aqp_children.relation_name, aqp_children.hash_cond, aqp_children.merge_cond, aqp_children.join_filter, aqp_children.recheck_cond)
                        reason = generate_why_cost(qep_children, aqp_children, QEP_cost, AQP_cost)
                        reasons.append(reason)
                        QEP_nodes.append(qep_children)
                        break

            if qep_children.node_type == 'Merge Join':
                join_cond = ''.join(sorted(qep_children.merge_cond))
                print(join_cond)
                if aqp_children.recheck_cond:
                    if join_cond == aqp_children.merge_cond or join_cond == ''.join(sorted(aqp_children.recheck_cond)):
                        print("In Merge Join")
                        print("QEP",qep_children.node_type, qep_children.relation_name, qep_children.hash_cond, qep_children.merge_cond)
                        print("AQP ",aqp_children.node_type, aqp_children.relation_name, aqp_children.hash_cond, aqp_children.merge_cond, aqp_children.join_filter, aqp_children.recheck_cond)
                        reason = generate_why_cost(qep_children, aqp_children, QEP_cost, AQP_cost)
                        reasons.append(reason)
                        QEP_nodes.append(qep_children)
                        break
                elif aqp_children.hash_cond:
                    if join_cond == aqp_children.merge_cond or join_cond == ''.join(sorted(aqp_children.hash_cond)):
                        print("In Merge Join")
                        print("QEP",qep_children.node_type, qep_children.relation_name, qep_children.hash_cond, qep_children.merge_cond)
                        print("AQP ",aqp_children.node_type, aqp_children.relation_name, aqp_children.hash_cond, aqp_children.merge_cond, aqp_children.join_filter, aqp_children.recheck_cond)
                        reason = generate_why_cost(qep_children, aqp_children, QEP_cost, AQP_cost)
                        reasons.append(reason)
                        QEP_nodes.append(qep_children)
                        break
                elif aqp_children.join_filter:
                    if join_cond == aqp_children.merge_cond or join_cond == ''.join(sorted(aqp_children.join_filter)):
                        print("In Merge Join")
                        print("QEP",qep_children.node_type, qep_children.relation_name, qep_children.hash_cond, qep_children.merge_cond)
                        print("AQP ",aqp_children.node_type, aqp_children.relation_name, aqp_children.hash_cond, aqp_children.merge_cond, aqp_children.join_filter, aqp_children.recheck_cond)
                        reason = generate_why_cost(qep_children, aqp_children, QEP_cost, AQP_cost)
                        reasons.append(reason)
                        QEP_nodes.append(qep_children)
                        break
                
            if qep_children.node_type == 'Nested Loop':
                if aqp_children.join_filter:
                    if qep_children.join_filter == aqp_children.join_filter:
                        print("In Nested Loop")
                        print("QEP",qep_children.node_type, qep_children.relation_name, qep_children.hash_cond, qep_children.merge_cond, qep_children.join_filter)
                        print("AQP ",aqp_children.node_type, aqp_children.relation_name, aqp_children.hash_cond, aqp_children.merge_cond, aqp_children.join_filter, aqp_children.recheck_cond)
                        reason = generate_why_cost(qep_children, aqp_children, QEP_cost, AQP_cost)
                        reasons.append(reason)
                        QEP_nodes.append(qep_children)
                        break
                elif aqp_children.recheck_cond:
                    if qep_children.join_filter == aqp_children.recheck_cond:
                        print("In Nested Loop")
                        print("QEP",qep_children.node_type, qep_children.relation_name, qep_children.join_filter)
                        print("AQP ",aqp_children.node_type, aqp_children.relation_name, aqp_children.join_filter, aqp_children.recheck_cond)
                        reason = generate_why_cost(qep_children, aqp_children, QEP_cost, AQP_cost)
                        reasons.append(reason)
                        QEP_nodes.append(qep_children)
                        break
                elif aqp_children.hash_cond:
                    if qep_children.join_filter == aqp_children.hash_cond:
                        print("In Nested Loop")
                        print("QEP",qep_children.node_type, qep_children.relation_name, qep_children.join_filter)
                        print("AQP ",aqp_children.node_type, aqp_children.relation_name, aqp_children.join_filter, aqp_children.hash_cond)
                        reason = generate_why_cost(qep_children, aqp_children, QEP_cost, AQP_cost)
                        reasons.append(reason)
                        QEP_nodes.append(qep_children)
                        break
                elif aqp_children.merge_cond:
                    if qep_children.join_filter == aqp_children.merge_cond:
                        print("In Nested Loop")
                        print("QEP",qep_children.node_type, qep_children.relation_name, qep_children.join_filter)
                        print("AQP ",aqp_children.node_type, aqp_children.relation_name, aqp_children.join_filter, aqp_children.merge_cond)
                        reason = generate_why_cost(qep_children, aqp_children, QEP_cost, AQP_cost)
                        reasons.append(reason)
                        QEP_nodes.append(qep_children)
                        break
        
            if qep_children.node_type == 'Sort':
                if qep_children.sort_key == aqp_children.sort_key:
                    reason = generate_why_cost(qep_children, aqp_children, QEP_cost, AQP_cost)
                    reasons.append(reason)
                    QEP_nodes.append(qep_children)
                    break
            
            if qep_children.node_type == 'Incremental Sort':
                if qep_children.sort_key == aqp_children.sort_key:
                    reason = generate_why_cost(qep_children, aqp_children, QEP_cost, AQP_cost)
                    reasons.append(reason)
                    QEP_nodes.append(qep_children)
                    break
            
            if qep_children.node_type == 'Aggregate':
                if qep_children.group_key == aqp_children.group_key:
                    reason = generate_why_cost(qep_children, aqp_children, QEP_cost, AQP_cost)
                    reasons.append(reason)
                    QEP_nodes.append(qep_children)
                    break

    # if QEP_children_no == AQP_children_no and QEP.node_type == AQP.node_type:
    #     if QEP_children_no != 0:
    #         for i in range(len(QEP_children)):
    #             check_why_children(QEP_children[i], AQP_children[i], reasons, QEP_cost, AQP_cost)
    
    # else:
    #     if QEP.node_type == 'Hash' or QEP.node_type == 'Sort':
    #         reason = generate_why_cost(QEP.children[0], AQP, QEP_cost, AQP_cost)
    #         reasons.append(reason)

    #     elif AQP.node_type == 'Hash' or AQP.node_type == 'Sort':
    #         reason = generate_why_cost(QEP, AQP.children[0], QEP_cost, AQP_cost)
    #         reasons.append(reason)

    #     elif QEP.node_type == 'Hash Join' or QEP.node_type == 'Merge Join' or QEP.node_type == 'Nested Loop':
    #         if QEP_children_no == 1 and AQP_children_no == 1:
    #             reason = generate_why_cost(QEP.children[0], AQP.children[0], QEP_cost, AQP_cost)
    #             reasons.append(reason)
    #         else:
    #             pass

    #     elif QEP.node_type == 'Seq Scan' or QEP.node_type == 'Index Scan' or QEP.node_type == 'Bitmap Heap Scan':
    #         if QEP.relation_name == AQP.relation_name:
    #             reason = generate_why_cost(QEP, AQP, QEP_cost, AQP_cost)
    #             reasons.append(reason)

    #     elif AQP.node_type == 'Hash Join' or AQP.node_type == 'Merge Join' or AQP.node_type == 'Nested Loop':
    #         reason = generate_why_cost(QEP, AQP.children[0], QEP_cost, AQP_cost)
    #         reasons.append(reason)
        
        
    #     elif AQP.node_type == 'Seq Scan' or AQP.node_type == 'Index Scan' or AQP.node_type == 'Bitmap Heap Scan':
    #         try:
    #             reason = generate_why_cost(QEP, AQP, QEP_cost, AQP_cost)
    #             reasons.append(reason)
    #         except:
    #             pass
    #     elif 'Gather' in QEP.node_type:
    #         check_why_children(QEP_children[0], AQP, reasons, QEP_cost, AQP_cost)

    #     elif 'Gather' in AQP.node_type:
    #         check_why_children(QEP, AQP_children[0], reasons, QEP_cost, AQP_cost)
    #     else:
    #         try:
    #             reason = generate_why_cost(QEP, AQP, QEP_cost, AQP_cost)
    #             reasons.append(reason)
    #         except:
    #             pass
            

    #     if QEP_children_no == AQP_children_no:
    #         if QEP_children_no == 1:
    #             check_why_children(QEP_children[0], AQP_children[0], reasons, QEP_cost, AQP_cost)
    #         if QEP_children_no == 2:
    #             check_why_children(QEP_children[0], AQP_children[0], reasons, QEP_cost, AQP_cost)
    #             check_why_children(QEP_children[1], AQP_children[1], reasons, QEP_cost, AQP_cost)

def get_why_cost(QEP, AQP, QEP_cost, AQP_cost):

    QEP = parse_json(QEP)[0]
    clear_cache()
    AQP = parse_json(AQP)[0]
    clear_cache()

    reasons = []
    QEP_nodes = []
    check_why_children(QEP, AQP, reasons, QEP_nodes, QEP_cost, AQP_cost)


    # reason_str = ""
    # for i in range (len(reasons)):
    #     reason_str = reason_str + reasons[i] + "\n\n"

    return reasons, QEP_nodes


def get_total_cost(json_obj):
    node = parse_json(json_obj)[0]
    return node.total_cost

def get_diff(json_obj_A, json_obj_B):
    global num
    head_node_a = parse_json(json_obj_A)[0]
    clear_cache()
    to_text(head_node_a)

    head_node_b = parse_json(json_obj_B)[0]
    clear_cache()
    to_text(head_node_b)

    num=1
    difference = []
    reasons = []
    check_children(head_node_a, head_node_b, difference, reasons)
    diff_str = ""
    for i in range (len(reasons)):
        diff_str = diff_str + difference[i] + "\n\n"
        if reasons[i] != "":
            diff_str = diff_str + reasons[i] + "\n" 
        if i != len(reasons)-1:
            diff_str = diff_str + "-"*200 + "\n"
    return diff_str