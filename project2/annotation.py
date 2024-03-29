import copy
from queue import Queue
from itertools import chain
try:
    from itertools import imap
except ImportError:
    imap=map

# Node class to store the information of each node in the query plan
class Node(object):
    def __init__(self, node_type, relation_name, schema, alias, group_key, sort_key, join_type, index_name, 
            hash_cond, table_filter, index_cond, merge_cond, recheck_cond, join_filter, subplan_name, actual_rows,
            description, cost, parent_relationship):
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
        self.description = description
        self.cost = cost
        self.parent_relationship = parent_relationship

    # Function to append the child node to the current node
    def add_children(self, child):
        self.children.append(child)
    
    # Function to set output name of the node
    def set_output_name(self, output_name):
        if "T" == output_name[0] and output_name[1:].isdigit():
            self.output_name = int(output_name[1:])
        else:
            self.output_name = output_name

    # Function to get output name of the node
    def get_output_name(self):
        if str(self.output_name).isdigit():
            return "T" + str(self.output_name)
        else:
            return self.output_name

    # Function to set the step number of the node
    def set_step(self, step):
        self.step = step
    
    # Function to map NLP description to the node
    def update_desc(self,desc):
        self.description = desc
    
    # Function to iterate over the node and its children
    def __iter__(self):
        for v in chain(*imap(iter, self.children)):
            yield v
        yield self
        
# Function to parse the JSON object and return the root node of the query plan
def parse_json(data):
    q = Queue()
    q_node = Queue()
    plan = data['Plan']
    q.put(plan)
    q_node.put(None)

    node_type_list = []
    node_total_cost = 0

    # Iterate over the queue to parse the JSON object
    while not q.empty():
        current_plan = q.get()
        parent_node = q_node.get()

        relation_name = schema = alias = group_key = sort_key = join_type = index_name = hash_cond = table_filter \
        = index_cond = merge_cond = recheck_cond = join_filter = subplan_name \
        = actual_rows = description = parent_relationship = None
        cost = 0

        # Check the infomration of the current node
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

        if 'Subplan Name' in current_plan:
            if "returns" in current_plan['Subplan Name']:
                name = current_plan['Subplan Name']
                subplan_name = name[name.index("$"):-1]
            else:
                subplan_name = current_plan['Subplan Name']

        if 'Total Cost' in current_plan:
            cost = current_plan['Total Cost']
        
        if 'Parent Relationship' in current_plan:
            parent_relationship = current_plan['Parent Relationship']

        # Create a new node with the information of the current node
        current_node = Node(current_plan['Node Type'], relation_name, schema, alias, group_key, sort_key, join_type,
                            index_name, hash_cond, table_filter, index_cond, merge_cond, recheck_cond, join_filter,
                            subplan_name, actual_rows, description, cost, parent_relationship)
        
        # Append the current node type to the list of node types
        node_type_list.append(current_node.node_type)

        # Add current node cost to the total cost
        node_total_cost += current_node.cost

        # Check for conditions to update the information of the node
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

    # Return the root node of the query plan, the list of node types and the total cost of the query plan
    return head_node, node_type_list, int(node_total_cost)


# Function to generate a new processed copy of the head node
def simplify_graph(node):
    new_node = copy.deepcopy(node)
    new_node.children = []

    for child in node.children:
        new_child = simplify_graph(child)
        new_node.add_children(new_child)

    if node.node_type in ["Result"]:
        return node.children[0]

    return new_node

# Function to clean up information of the node
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


# Function to generate the NLP description of the node
def to_text(node, skip=False):
    global steps, cur_step, cur_table_name
    increment = True

    # Skip the child if merge it with current node
    if node.node_type in ["Unique", "Aggregate"] and len(node.children) == 1 \
            and ("Scan" in node.children[0].node_type or node.children[0].node_type == "Sort"):
        children_skip = True
    elif node.node_type == "Bitmap Heap Scan" and node.children[0].node_type == "Bitmap Index Scan":
        children_skip = True
    else:
        children_skip = False

    # Recursively generate the NLP description of the child nodes
    for child in node.children:
        if node.node_type == "Aggregate" and len(node.children) > 1 and child.node_type == "Sort":
            to_text(child, True)
        else:
            to_text(child, children_skip)

    if node.node_type in ["Hash"] or skip:
        return

    step = ""

    # Generate customised NLP for various QEP operators
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
        # Combine bitmap heap scan and bitmap index scan
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

        # If no table filter, remain original table name
        if not node.table_filter:
            increment = False

    elif node.node_type == "Unique":
        # Combine unique and sort
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
            # Combine aggregate and sort
            if "Sort" in child.node_type:
                child.set_output_name(child.children[0].get_output_name())
                step = "sort " + child.get_output_name() + " and "
            # Combine aggregate with scan
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
        # Binary operator
        if len(node.children) > 1:
            for i, child in enumerate(node.children):
                if i < len(node.children) - 1:
                    step += (" table " + child.get_output_name() + ",")
                else:
                    step += (" and table " + child.get_output_name())
        # Unary operator
        else:
            step += " table " + node.children[0].get_output_name()
    if node.cost:
            step += " with cost " + str(node.cost)
            
    # Add more conditions
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

    # Set intermediate table name
    if increment:
        node.set_output_name("T" + str(cur_table_name))
        step += " to get intermediate table " + node.get_output_name()
        cur_table_name += 1
    if node.subplan_name:
        table_subquery_name_pair[node.subplan_name] = node.get_output_name()

    # Add NLP description to the description attribute of the node
    node.update_desc(step)
    step = "Step " + str(cur_step) + ". " + step + "."

    # Add step to the step attribute of the node to indicate the order of execution
    node.set_step(cur_step)
    cur_step += 1

    steps.append(step)


# Function to get the NLP description of the plan
def get_text(json_obj):
    global steps, cur_step, cur_table_name, table_subquery_name_pair
    global current_plan_tree
    steps = ["The query is executed as follow."]
    cur_step = 1
    cur_table_name = 1
    table_subquery_name_pair = {}

    # Parse the JSON object
    head_node = parse_json(json_obj)[0]

    # Process the head node
    simplified_graph = simplify_graph(head_node)

    # Generate the NLP description of the plan
    to_text(simplified_graph)
    if " to get intermediate table" in steps[-1]:
        steps[-1] = steps[-1][:steps[-1].index(
            " to get intermediate table")] + ' to get the final result.'

    return steps

# Reset the global variables for the NLP description of the next query
def clear_cache():
    global steps, cur_step, cur_table_name, table_subquery_name_pair
    steps = []
    cur_step = 1
    cur_table_name = 1
    table_subquery_name_pair = {}

# Function to generate customised NLP description of the reasons why the operator/node is chosen
def generate_reason(QEP, AQP, QEP_cost, AQP_cost):
    global text 
    text = ""
    
    # 3 cases:
    # 1. QEP.cost < AQP.cost
    # 2. QEP.cost = AQP.cost
    # 3. QEP.cost > AQP.cost
    # Check for the type of the operator
    # If the operator is a scan operator, check the table name
    if QEP.node_type in ['Seq Scan', 'Bitmap Heap Scan']:
        if QEP.cost < AQP.cost:
            text += " " + QEP.relation_name + " is read using " + QEP.node_type + " because: \n" \
                    " The cost of " + QEP.node_type + \
                    " , which is " + str(QEP.cost) + " is lower than the cost of " + AQP.node_type + "\n"\
                    " , which is " + str(AQP.cost) + ". "
        elif QEP.cost == AQP.cost:
            text += " " + QEP.relation_name + " is read using " + QEP.node_type + " because: \n"\
                    " Although the cost of reading " + QEP.relation_name + " using " + QEP.node_type + "\n"\
                    " ," + str(QEP.cost) + ", is equal to the cost of reading " + QEP.relation_name + " using " + AQP.node_type + "\n"\
                    " which is " + str(AQP.cost) + ", the total cost of the QEP is " + str(QEP_cost) + "\n"\
                    " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
        else:
            text += " " + QEP.relation_name + " is read using " + QEP.node_type + " because: \n"\
                    " Although the cost of reading " + QEP.relation_name + " using " + QEP.node_type + "\n"\
                    " ," + str(QEP.cost) + ", is higher than the cost of reading " + QEP.relation_name + " using " + AQP.node_type + "\n"\
                    " which is " + str(AQP.cost) + ", the total cost of the QEP is " + str(QEP_cost) + "\n"\
                    " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
    
    # If operator is in Index Scan or BitMap Index Scan, check the index cond for join condition
    # If index cond is None, check the index name for scan condition
    elif QEP.node_type in ['Index Scan', 'Bitmap Index Scan']:
        if QEP.index_cond:
            if QEP.cost < AQP.cost:
                text += " This join is implemented using Nested Loop with " + QEP.parent_relationship + " " + QEP.node_type+ " because: \n"\
                        " The cost of " \
                        " joining " + QEP.index_cond + " using Nested Loop with inner " + QEP.node_type + " is " + str(QEP.cost) + "\n"\
                            " which is lower than the cost of using Nested Loop with " + AQP.parent_relationship + " " + AQP.node_type + " which is " + str(AQP.cost) + ". "
            
            elif QEP.cost == AQP.cost:
                text += " This join is implemented using Nested Loop with "+ QEP.parent_relationship + " " + QEP.node_type+ " because: \n"\
                        " Although the cost of joining " + QEP.index_cond + " using Nested Loop with "+ QEP.parent_relationship + " " + QEP.node_type + " is " + str(QEP.cost) + "\n"\
                        " which is equal to the cost of using Nested Loop with " + AQP.parent_relationship + " " +  AQP.node_type + " which is " + str(AQP.cost) + "\n"\
                        ", the total cost of the QEP is " + str(QEP_cost) + \
                        " which is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
            else:
                text += " This join is implemented using Nested Loop with "+ QEP.parent_relationship + " " + QEP.node_type+ " because: \n"\
                        " Although the cost of joining " + QEP.index_cond + " using Nested Loop Join with "+ QEP.parent_relationship + " " + QEP.node_type + " is " + str(QEP.cost) + "\n"\
                        " which is higher than the cost of using Nested Loop " + AQP.parent_relationship + " " + AQP.node_type + " which is " + str(AQP.cost) + "\n"\
                        ", the total cost of the QEP is " + str(QEP_cost) + \
                        " which is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
        else:
            if QEP.cost < AQP.cost:
                text += " " + QEP.relation_name + " is read using " + QEP.node_type + " because: \n" \
                    " The cost of " + QEP.node_type + \
                    " , which is " + str(QEP.cost) + " is lower than the cost of " + AQP.node_type + "\n"\
                    " , which is " + str(AQP.cost) + ". "
            elif QEP.cost == AQP.cost:
                text += " " + QEP.relation_name + " is read using " + QEP.node_type + " because: \n"\
                        " Although the cost of reading " + QEP.relation_name + " using " + QEP.node_type + "\n"\
                        " ," + str(QEP.cost) + ", is equal to the cost of reading " + QEP.relation_name + " using " + AQP.node_type + "\n"\
                        " which is " + str(AQP.cost) + ", the total cost of the QEP is " + str(QEP_cost) + "\n"\
                        " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
            else:
                text += " " + QEP.relation_name + " is read using " + QEP.node_type + " because: \n"\
                        " Although the cost of reading " + QEP.relation_name + " using " + QEP.node_type + "\n"\
                        " ," + str(QEP.cost) + ", is higher than the cost of reading " + QEP.relation_name + " using " + AQP.node_type + "\n"\
                        " which is " + str(AQP.cost) + ", the total cost of the QEP is " + str(QEP_cost) + "\n"\
                        " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
    
    # If operator is in Hash Join, check the join condition
    # Check against the various join types
    elif QEP.node_type in ['Hash Join', 'Merge Join', 'Nested Loop']:
        if QEP.cost < AQP.cost:
            if QEP.hash_cond:
                if AQP.hash_cond or AQP.merge_cond:
                    text += " This join is implemented using " + QEP.node_type + " because: \n"\
                            " The cost of "+ QEP.node_type + \
                            " joining " + QEP.hash_cond + " is " + str(QEP.cost) + "\n"\
                            " which is lower than the cost of using " + AQP.node_type + " which is " + str(AQP.cost) + ". "
                elif AQP.recheck_cond or AQP.index_cond:
                    text += " This join is implemented using " + QEP.node_type + " because: \n"\
                            " The cost of "+ QEP.node_type + \
                            " joining " + QEP.hash_cond + " is " + str(QEP.cost) + "\n"\
                            " which is lower than the cost of using Nested Loop Join with "+ AQP.parent_relationship + " " + AQP.node_type + \
                            " which is " + str(AQP.cost) + ". "
                else:
                    text += " This join is implemented using " + QEP.node_type + " because: \n" \
                            " The cost of "+ QEP.node_type + \
                            " joining " + QEP.hash_cond + " is " + str(QEP.cost) + "\n"\
                            " which is lower than the cost of using Nested Loop Join which is " + str(AQP.cost) + ". "
            elif QEP.merge_cond:
                if AQP.hash_cond or AQP.merge_cond:
                    text += " This join is implemented using " + QEP.node_type + " because: \n" \
                            " The cost of "+ QEP.node_type + \
                            " joining " + QEP.merge_cond + " is " + str(QEP.cost) + "\n"\
                            + " which is lower than the cost of using " + AQP.node_type + " which is " + str(AQP.cost) + ". "
                elif AQP.recheck_cond or AQP.index_cond:
                    text += " This join is implemented using " + QEP.node_type + " because: \n" \
                            " The cost of "+ QEP.node_type + \
                            " joining " + QEP.merge_cond + " is " + str(QEP.cost) + "\n"\
                            " which is lower than the cost of using Nested Loop Join with "+ AQP.parent_relationship + " " + AQP.node_type + \
                            " which is " + str(AQP.cost) + ". "
                else:
                    text += " This join is implemented using " + QEP.node_type + " because: \n" \
                            " The cost of "+ QEP.node_type + \
                            " joining " + QEP.merge_cond + " is " + str(QEP.cost) + "\n"\
                            " which is lower than the cost " + " of using Nested Loop which is " + str(AQP.cost) + ". "
            else:
               text += " This join is implemented using " + QEP.node_type + " because: \n" \
                       " The cost of "+ QEP.node_type + \
                       " joining is " + str(QEP.cost) + " \n which is lower than the cost of using " + AQP.node_type + \
                       " which is " + str(AQP.cost) + ". "
    
        elif QEP.cost == AQP.cost:
            if QEP.hash_cond:
                if AQP.hash_cond or AQP.merge_cond:
                    text += " This join is implemented using " + QEP.node_type + " because: \n"\
                            " Although the cost of "+ QEP.node_type + " joining " + QEP.hash_cond + " , " + str(QEP.cost) + "\n"\
                            " , is same as " + AQP.node_type + " , with cost " + str(AQP.cost) + ". " + "\n"\
                            " the total cost of the QEP is " + str(QEP_cost) + "\n"\
                            " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
                elif AQP.recheck_cond or AQP.index_cond:
                    text += " This join is implemented using " + QEP.node_type + " because: \n"\
                            " Although the cost of "+ QEP.node_type + " joining " + QEP.hash_cond + " , " + str(QEP.cost) + "\n"\
                            " , is same as Nested Loop Join with "+ AQP.parent_relationship + " " + AQP.node_type + " , with cost " + str(AQP.cost) + ". " + "\n"\
                            " the total cost of the QEP is " + str(QEP_cost) + "\n"\
                            " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
                else:
                    text += " This join is implemented using " + QEP.node_type + " because: \n"\
                            " Although the cost of "+ QEP.node_type + " joining " + QEP.hash_cond + " , " + str(QEP.cost) + "\n"\
                            " , is same as "+ AQP.node_type + " , with cost " + str(AQP.cost) + "\n"\
                            " , followed by Memoize and Nested Loop. " + "\n"\
                            " the total cost of the QEP is " + str(QEP_cost) + "\n"\
                            " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
            
            elif QEP.merge_cond:
                if AQP.hash_cond or AQP.merge_cond:
                    text += " This join is implemented using " + QEP.node_type + " because: \n"\
                            " Although the cost of "+ QEP.node_type + " joining " + QEP.merge_cond + " , " + str(QEP.cost) + "\n"\
                            " , is same as " + AQP.node_type + " , with cost " + str(AQP.cost) + ", " + "\n"\
                            " the total cost of the QEP is " + str(QEP_cost) + "\n"\
                            " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
                elif AQP.recheck_cond or AQP.index_cond:
                    text += " This join is implemented using " + QEP.node_type + " because: \n"\
                            " Although the cost of "+ QEP.node_type + " joining " + QEP.merge_cond + " , " + str(QEP.cost) + "\n"\
                            " , is same as Nested Loop Join with "+ AQP.parent_relationship + " " + AQP.node_type + " , with cost " + str(AQP.cost) + ". " + "\n"\
                            " the total cost of the QEP is " + str(QEP_cost) + "\n"\
                            " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
                else:
                    text += " This join is implemented using " + QEP.node_type + " because: \n"\
                            " Although the cost of "+ QEP.node_type + " joining " + QEP.hash_cond + " , " + str(QEP.cost) + "\n"\
                            " , is same as "+ AQP.node_type + " , with cost " + str(AQP.cost) + "\n"\
                            " , followed by Memoize and Nested Loop, " + "\n"\
                            " the total cost of the QEP is " + str(QEP_cost) + "\n"\
                            " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
            else:
                text += " This join is implemented using " + QEP.node_type + " because: \n"\
                        " Although the cost of "+ QEP.node_type + " , " + str(QEP.cost) + "\n"\
                        " , is same as " + AQP.node_type + " , with cost " + str(AQP.cost) + ", " + "\n"\
                        " the total cost of the QEP is " + str(QEP_cost) + "\n"\
                        " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
    
        else:
            if QEP.hash_cond:
                if AQP.hash_cond or AQP.merge_cond:
                    text += " This join is implemented using " + QEP.node_type + " because: \n"\
                            " Although the cost of joining " + QEP.hash_cond + " using " + QEP.node_type + "\n"\
                            " ," + str(QEP.cost) + ", is higher than the cost of joining " + QEP.hash_cond + "\n"\
                            " using " + AQP.node_type + " with cost " + str(AQP.cost) + "\n"\
                            " , the total cost of the QEP is " + str(QEP_cost) + "\n"\
                            " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
                elif AQP.recheck_cond or AQP.index_cond:
                    text += " This join is implemented using " + QEP.node_type + " because: \n"\
                            " Although the cost of joining " + QEP.hash_cond + " using " + QEP.node_type + "\n"\
                            " ," + str(QEP.cost) + ", is higher than the cost of joining " + QEP.hash_cond + "\n"\
                            " using Nested Loop Join with "+ AQP.parent_relationship + " " + AQP.node_type + " with cost " + str(AQP.cost) + "\n"\
                            " , the total cost of the QEP is " + str(QEP_cost) + "\n"\
                            " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
                else:
                    text += " This join is implemented using " + QEP.node_type + " because: \n"\
                            " Although the cost of joining " + QEP.hash_cond + " using " + QEP.node_type + "\n"\
                            " ," + str(QEP.cost) + ", is higher than the cost of joining"+ \
                            " using " + AQP.node_type + " with cost " + str(AQP.cost) + "\n"\
                            " followed by Memoize and Nested Loop, \n the total cost of the QEP is " + str(QEP_cost) + \
                            " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
            elif QEP.merge_cond:
                if AQP.hash_cond or AQP.merge_cond:
                    text += " This join is implemented using " + QEP.node_type + " because: \n"\
                            " Although the cost of joining " + QEP.merge_cond + " using " + QEP.node_type + "\n"\
                            " ," + str(QEP.cost) + ", is higher than the cost of joining " + QEP.merge_cond + "\n"\
                            " using " + AQP.node_type + " with cost " + str(AQP.cost) + "\n"\
                            " , the total cost of the QEP is " + str(QEP_cost) + "\n"\
                            " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
                elif AQP.recheck_cond or AQP.index_cond:
                    text += " This join is implemented using " + QEP.node_type + " because: \n"\
                            " Although the cost of joining " + QEP.merge_cond + " using " + QEP.node_type + "\n"\
                            " ," + str(QEP.cost) + ", is higher than the cost of joining " + QEP.merge_cond + "\n"\
                            " using Nested Loop Join with "+ AQP.parent_relationship + " " + AQP.node_type + " with cost " + str(AQP.cost) + "\n"\
                            " , the total cost of the QEP is " + str(QEP_cost) + "\n"\
                            " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
                else:
                    text += " This join is implemented using " + QEP.node_type + " because: \n"\
                            " Although the cost of joining " + QEP.merge_cond + " using " + QEP.node_type + "\n"\
                            " ," + str(QEP.cost) + ", is higher than the cost of joining" + "\n"\
                            " using " + AQP.node_type + \
                            " followed by Memoize and Nested Loop, \nthe total cost of the QEP is " + str(QEP_cost) + \
                            " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
            else:
                text += " This join is implemented using " + QEP.node_type + " because: \n"\
                        " Although the cost of joining using " + QEP.node_type + " ," + str(QEP.cost) + "\n"\
                        " ,is higher than the cost of joining using " + AQP.node_type + "\n"\
                        " which is " + str(AQP.cost) + ", the total cost of the QEP is " + str(QEP_cost) + "\n"\
                        " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
    
    elif QEP.node_type in ['Gather','Aggregate', 'Gather Merge']:
        text += " " + QEP.node_type + " is used because: \n"\
                " The cost of using " + QEP.node_type + " is " + str(QEP.cost) + "\n"\
                " and there are no other alternatives to implement this query. "

    # If the operator is a sort, check the sort keys
    elif QEP.node_type in ['Sort', 'Incremental Sort']:
        for i in range(len(QEP.sort_key)):
            if '::' in (QEP.sort_key)[i]:
                (QEP.sort_key)[i] = ((QEP.sort_key)[i]).replace('::', '. ')
                break

        if QEP.cost < AQP.cost:
            text += " This sort is implemented using " + QEP.node_type + " because: \n" \
                    " The cost of "+ QEP.node_type + \
                    " sorting " + ' '.join(QEP.sort_key) + " is " + str(QEP.cost) + "\n"\
                    " which is less than the cost " + " of using " + AQP.node_type + \
                    " which is " + str(AQP.cost) + ". "
        elif QEP.cost == AQP.cost:
            text += " This sort is implemented using " + QEP.node_type + " because: \n"\
                    " Although the cost of "+ QEP.node_type + " sorting " + QEP.sort_key + " , " + str(QEP.cost) + "\n"\
                    " ,is same as " + AQP.node_type + " , with cost " + str(AQP.cost) + ", " + "\n"\
                    " the total cost of the QEP is " + str(QEP_cost) + "\n"\
                    " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
        else:
           text +=  " This sort is implemented using " + QEP.node_type + " because: \n"\
                    " Although the cost of "+ QEP.node_type + " , " + str(QEP.cost) + "\n"\
                    " , is higher than " + AQP.node_type + " , with cost " + str(AQP.cost) + ", " + "\n"\
                    " the total cost of the QEP is " + str(QEP_cost) + "\n"\
                    " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
    
    # No other operators are available
    else:
        if QEP.cost < AQP.cost:
            if QEP.relation_name:
                text += " The cost of " + QEP.node_type + " on " + QEP.relation_name + " is " + str(QEP.cost) + "\n"\
                        " which is lower than the cost of using " + AQP.node_type + " which is " + str(AQP.cost) + ". "
            else:
                text += " The cost of " + QEP.node_type + " is " + str(QEP.cost) + "\n"\
                        " which is lower than the cost of using " + AQP.node_type + " which is " + str(AQP.cost) + ". "

        elif QEP.cost == AQP.cost:
            if QEP.relation_name:
                text += " The cost of " + QEP.node_type + " on " + QEP.relation_name + " is " + str(QEP.cost) + "\n"\
                        " which is same as the cost of using " + AQP.node_type + " which is " + str(AQP.cost) + ". " + "\n" \
                        " However, the total cost of the QEP is " + str(QEP_cost) + " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
            else:
                text += " The cost of " + QEP.node_type + " is " + str(QEP.cost) + "\n"\
                        " which is same as the cost of using " + AQP.node_type + " which is " + str(AQP.cost) + ". " + "\n"\
                        " However, the total cost of the QEP is " + str(QEP_cost) + " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
        else:
            if QEP.relation_name:
                text += " The cost of " + QEP.node_type + " on " + QEP.relation_name + " is " + str(QEP.cost) + "\n"\
                        " which is higher than the cost of using " + AQP.node_type + " which is " + str(AQP.cost) + ". " + "\n"\
                        " However, the total cost of the QEP is " + str(QEP_cost) + " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "
            else:
                text += " The cost of " + QEP.node_type + " is " + str(QEP.cost) + "\n"\
                        " which is higher than the cost of using " + AQP.node_type + " which is " + str(AQP.cost) + ". " + "\n"\
                        " However, the total cost of the QEP is " + str(QEP_cost) + " is lower than the total cost of the AQP, which is " + str(AQP_cost) + ". "

    return text

# Function to iterate through the QEP and AQP,compare and map the nodes to generate the reasons
def compare_node(QEP_head, AQP_head, reasons, QEP_nodes, QEP_cost, AQP_cost):


    QEP_node_list = list(iter(QEP_head))
    AQP_node_list = list(iter(AQP_head))
    
    # For each node in the QEP, find the corresponding node in the AQP, if any
    for i in range(len(QEP_node_list)):
        for j in range(len(AQP_node_list)): 

            # If the node is a scan, check the relation name against the respective attribute of other scan nodes in the AQP
            if QEP_node_list[i].node_type in ['Seq Scan', 'Bitmap Heap Scan', 'Bitmap Index Scan', 'CTE Scan']:
                if QEP_node_list[i].relation_name == AQP_node_list[j].relation_name or QEP_node_list[i].relation_name == AQP_node_list[j].index_name:
                    reason = generate_reason(QEP_node_list[i], AQP_node_list[j], QEP_cost, AQP_cost)
                    reasons.append(reason)
                    QEP_nodes.append(QEP_node_list[i])
                    break
                
            # If the node is a Index Scan, check the index cond against the respective attributes of other join nodes in the AQP
            # Also check the index name against the respective attributes of other scan nodes in the AQP
            if QEP_node_list[i].node_type == 'Index Scan':
                if QEP_node_list[i].index_cond:
                    join_cond = ''.join(sorted(QEP_node_list[i].index_cond))
                    if AQP_node_list[j].hash_cond:
                        if QEP_node_list[i].index_cond == AQP_node_list[j].hash_cond or join_cond == ''.join(sorted(AQP_node_list[j].hash_cond)):
                            reason = generate_reason(QEP_node_list[i], AQP_node_list[j], QEP_cost, AQP_cost)
                            reasons.append(reason)
                            QEP_nodes.append(QEP_node_list[i])
                            break
                    if AQP_node_list[j].merge_cond:
                        if QEP_node_list[i].index_cond == AQP_node_list[j].merge_cond or join_cond == ''.join(sorted(AQP_node_list[j].merge_cond)):
                            reason = generate_reason(QEP_node_list[i], AQP_node_list[j], QEP_cost, AQP_cost)
                            reasons.append(reason)
                            QEP_nodes.append(QEP_node_list[i])
                            break
                    
                    if AQP_node_list[j].recheck_cond:
                        if QEP_node_list[i].index_cond == AQP_node_list[j].recheck_cond or join_cond == ''.join(sorted(AQP_node_list[j].recheck_cond)):
                            QEP_node_list[i].cost += int(QEP_node_list[i+1].cost)
                            for k in range(j+1, len(AQP_node_list)):
                                if AQP_node_list[k].node_type == 'Nested Loop':
                                    AQP_node_list[j].cost += int(AQP_node_list[k].cost)
                                    break
                            reason = generate_reason(QEP_node_list[i], AQP_node_list[j], QEP_cost, AQP_cost)
                            reasons.append(reason)
                            QEP_nodes.append(QEP_node_list[i])
                            break
                else:
                    if QEP_node_list[i].relation_name == AQP_node_list[j].relation_name or QEP_node_list[i].index_name == AQP_node_list[j].relation_name or QEP_node_list[i].index_name == AQP_node_list[j].index_name:
                        reason = generate_reason(QEP_node_list[i], AQP_node_list[j], QEP_cost, AQP_cost)
                        reasons.append(reason)
                        QEP_nodes.append(QEP_node_list[i])
                        break
            
            # If the node is a hash join, check the hash cond against the respective attributes of other join nodes in the AQP
            if QEP_node_list[i].node_type == 'Hash Join':
                join_cond = ''.join(sorted(QEP_node_list[i].hash_cond))
                if AQP_node_list[j].recheck_cond:
                    if QEP_node_list[i].hash_cond == AQP_node_list[j].recheck_cond or join_cond == ''.join(sorted(AQP_node_list[j].recheck_cond)):
                        for k in range(j+1, len(AQP_node_list)):
                            if AQP_node_list[k].node_type == 'Nested Loop':
                                AQP_node_list[j].cost += int(AQP_node_list[k].cost)
                                break
                        reason = generate_reason(QEP_node_list[i], AQP_node_list[j], QEP_cost, AQP_cost)
                        reasons.append(reason)
                        QEP_nodes.append(QEP_node_list[i])
                        break
                elif AQP_node_list[j].merge_cond:
                    if QEP_node_list[i].hash_cond == AQP_node_list[j].merge_cond or join_cond == ''.join(sorted(AQP_node_list[j].merge_cond)):
                        print("In Hash Join")
                        print("QEP",QEP_node_list[i].node_type, QEP_node_list[i].relation_name, QEP_node_list[i].hash_cond, QEP_node_list[i].merge_cond)
                        print("AQP ",AQP_node_list[j].node_type, AQP_node_list[j].relation_name, AQP_node_list[j].hash_cond, AQP_node_list[j].merge_cond, AQP_node_list[j].join_filter, AQP_node_list[j].recheck_cond)
                        reason = generate_reason(QEP_node_list[i], AQP_node_list[j], QEP_cost, AQP_cost)
                        reasons.append(reason)
                        QEP_nodes.append(QEP_node_list[i])
                        break
                elif AQP_node_list[j].join_filter:
                    if QEP_node_list[i].hash_cond == AQP_node_list[j].join_filter or join_cond == ''.join(sorted(AQP_node_list[j].join_filter)):
                        reason = generate_reason(QEP_node_list[i], AQP_node_list[j], QEP_cost, AQP_cost)
                        reasons.append(reason)
                        QEP_nodes.append(QEP_node_list[i])
                        break
                elif AQP_node_list[j].index_cond:
                    if QEP_node_list[i].hash_cond == AQP_node_list[j].index_cond or join_cond == ''.join(sorted(AQP_node_list[j].index_cond)):
                        for k in range(j+1, len(AQP_node_list)):
                            if AQP_node_list[k].node_type == 'Nested Loop':
                                AQP_node_list[j].cost += int(AQP_node_list[k].cost)
                                break
                        reason = generate_reason(QEP_node_list[i], AQP_node_list[j], QEP_cost, AQP_cost)
                        reasons.append(reason)
                        QEP_nodes.append(QEP_node_list[i])
                        break
            
            # If the node is a merge join, check the merge cond against the respective attributes of other join nodes in the AQP
            if QEP_node_list[i].node_type == 'Merge Join':
                join_cond = ''.join(sorted(QEP_node_list[i].merge_cond))
                if AQP_node_list[j].recheck_cond:
                    if QEP_node_list[i].merge_cond == AQP_node_list[j].recheck_cond or join_cond == ''.join(sorted(AQP_node_list[j].recheck_cond)):
                        for k in range(j+1, len(AQP_node_list)):
                                if AQP_node_list[k].node_type == 'Nested Loop':
                                    AQP_node_list[j].cost += int(AQP_node_list[k].cost)
                                    break
                        reason = generate_reason(QEP_node_list[i], AQP_node_list[j], QEP_cost, AQP_cost)
                        reasons.append(reason)
                        QEP_nodes.append(QEP_node_list[i])
                        break
                elif AQP_node_list[j].hash_cond:
                    if QEP_node_list[i].merge_cond == AQP_node_list[j].hash_cond or join_cond == ''.join(sorted(AQP_node_list[j].hash_cond)):
                        reason = generate_reason(QEP_node_list[i], AQP_node_list[j], QEP_cost, AQP_cost)
                        reasons.append(reason)
                        QEP_nodes.append(QEP_node_list[i])
                        break
                elif AQP_node_list[j].join_filter:
                    if QEP_node_list[i].merge_cond == AQP_node_list[j].join_filter or join_cond == ''.join(sorted(AQP_node_list[j].join_filter)):
                        reason = generate_reason(QEP_node_list[i], AQP_node_list[j], QEP_cost, AQP_cost)
                        reasons.append(reason)
                        QEP_nodes.append(QEP_node_list[i])
                        break
                elif AQP_node_list[j].index_cond:
                    if QEP_node_list[i].merge_cond == AQP_node_list[j].index_cond or join_cond == ''.join(sorted(AQP_node_list[j].index_cond)):
                        for k in range(j+1, len(AQP_node_list)):
                            if AQP_node_list[k].node_type == 'Nested Loop':
                                AQP_node_list[j].cost += int(AQP_node_list[k].cost)
                                break
                        reason = generate_reason(QEP_node_list[i], AQP_node_list[j], QEP_cost, AQP_cost)
                        reasons.append(reason)
                        QEP_nodes.append(QEP_node_list[i])
                        break
            
            # If the node is a nested loop, check the join_filter against the respective attributes of other join nodes in the AQP
            if QEP_node_list[i].node_type == 'Nested Loop':
                if QEP_node_list[i].join_filter:
                    join_cond = ''.join(sorted(QEP_node_list[i].join_filter))
                    if AQP_node_list[j].join_filter: 
                        if QEP_node_list[i].join_filter == AQP_node_list[j].join_filter or join_cond == ''.join(sorted(AQP_node_list[j].join_filter)):
                            reason = generate_reason(QEP_node_list[i], AQP_node_list[j], QEP_cost, AQP_cost)
                            reasons.append(reason)
                            QEP_nodes.append(QEP_node_list[i])
                            break
                    elif AQP_node_list[j].recheck_cond:
                        if QEP_node_list[i].join_filter == AQP_node_list[j].recheck_cond or join_cond == ''.join(sorted(AQP_node_list[j].recheck_cond)):
                            reason = generate_reason(QEP_node_list[i], AQP_node_list[j], QEP_cost, AQP_cost)
                            reasons.append(reason)
                            QEP_nodes.append(QEP_node_list[i])
                            break
                    elif AQP_node_list[j].hash_cond:
                        if QEP_node_list[i].join_filter == AQP_node_list[j].hash_cond or join_cond == ''.join(sorted(AQP_node_list[j].hash_cond)):
                            reason = generate_reason(QEP_node_list[i], AQP_node_list[j], QEP_cost, AQP_cost)
                            reasons.append(reason)
                            QEP_nodes.append(QEP_node_list[i])
                            break
                    elif AQP_node_list[j].merge_cond:
                        if QEP_node_list[i].join_filter == AQP_node_list[j].merge_cond or join_cond == ''.join(sorted(AQP_node_list[j].merge_cond)):
                            reason = generate_reason(QEP_node_list[i], AQP_node_list[j], QEP_cost, AQP_cost)
                            reasons.append(reason)
                            QEP_nodes.append(QEP_node_list[i])
                            break
                else:
                    if AQP_node_list[j].join_filter:
                        if QEP_node_list[i].join_filter == AQP_node_list[j].join_filter:
                            reason = generate_reason(QEP_node_list[i], AQP_node_list[j], QEP_cost, AQP_cost)
                            reasons.append(reason)
                            QEP_nodes.append(QEP_node_list[i])
                            break
                    elif AQP_node_list[j].recheck_cond:
                        if QEP_node_list[i].join_filter == AQP_node_list[j].recheck_cond:
                            reason = generate_reason(QEP_node_list[i], AQP_node_list[j], QEP_cost, AQP_cost)
                            reasons.append(reason)
                            QEP_nodes.append(QEP_node_list[i])
                            break
                    elif AQP_node_list[j].hash_cond:
                        if QEP_node_list[i].join_filter == AQP_node_list[j].hash_cond:
                            reason = generate_reason(QEP_node_list[i], AQP_node_list[j], QEP_cost, AQP_cost)
                            reasons.append(reason)
                            QEP_nodes.append(QEP_node_list[i])
                            break
                    elif AQP_node_list[j].merge_cond:
                        if QEP_node_list[i].join_filter == AQP_node_list[j].merge_cond:
                            reason = generate_reason(QEP_node_list[i], AQP_node_list[j], QEP_cost, AQP_cost)
                            reasons.append(reason)
                            QEP_nodes.append(QEP_node_list[i])
                            break
            
            # If the node is a sort, check the sort key against the respective attributes of other sort nodes in the AQP
            if QEP_node_list[i].node_type in ['Sort', 'Incremental Sort']:
                if QEP_node_list[i].sort_key == AQP_node_list[j].sort_key:
                    reason = generate_reason(QEP_node_list[i], AQP_node_list[j], QEP_cost, AQP_cost)
                    reasons.append(reason)
                    QEP_nodes.append(QEP_node_list[i])
                    break
            
            # If the node is an aggregate, check the group key against the respective attributes of other aggregate nodes in the AQP
            if QEP_node_list[i].node_type == 'Aggregate':
                if QEP_node_list[i].group_key == AQP_node_list[j].group_key:
                    reason = generate_reason(QEP_node_list[i], AQP_node_list[j], QEP_cost, AQP_cost)
                    reasons.append(reason)
                    QEP_nodes.append(QEP_node_list[i])
                    break
            
            if QEP_node_list[i].node_type == 'Gather':
                reason = generate_reason(QEP_node_list[i], AQP_node_list[j], QEP_cost, AQP_cost)
                reasons.append(reason)
                QEP_nodes.append(QEP_node_list[i])
                break


# Function to get the reasons for the operator choice in the QEP
def get_reason(QEP, AQP, QEP_cost, AQP_cost):

    QEP_head = parse_json(QEP)[0]
    clear_cache()
    AQP_head = parse_json(AQP)[0]
    clear_cache()

    reasons = []
    QEP_nodes = []
    compare_node(QEP_head, AQP_head, reasons, QEP_nodes, QEP_cost, AQP_cost)

    # Return the reasons for the operator choice in the QEP and the nodes in the QEP that have been compared
    return reasons, QEP_nodes

