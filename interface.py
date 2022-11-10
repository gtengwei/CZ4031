from winreg import QueryInfoKey
import PySimpleGUI as sg
import time
from PIL import Image, ImageTk
from preprocessing import *
from time import sleep
import threading

# Add a touch of color
sg.theme('DarkBlue3')   

# Change font and font size
sg.set_options(font=('Helvetica', 12)) #

# Default size for frames, can be changed
WIDTH = 500
HEIGHT = 700

query = ''

# Blank frame for testing purposes
def blank_frame():
    return sg.Frame("", [[]], pad=(5, 3), expand_x=True, expand_y=True, background_color='#404040', border_width=0)

# Resize image generated for QEP to fit in the frame
def resize_image(image, width, height):
    image = Image.open(image)
    image = image.resize((width, height), resample = Image.Resampling.LANCZOS)
    return image
    
# Move window to the center of the screen
def move_center(window):
    print(window.current_location())
    screen_width, screen_height = window.get_screen_dimensions()
    win_width, win_height = window.size
    x, y = (screen_width - win_width)//2, (screen_height - win_height)//2
    window.move(x, y)

# Update tooltip text
def update(element, text):
    element.TooltipObject.text = text

# Popup loading message
def popup(message):
    sg.theme('DarkGrey')
    layout = [[sg.Text(message)]]
    window = sg.Window('Message', layout, no_titlebar=True, keep_on_top=True, finalize=True)
    return window

# Build the GUI
def build():
    
    # Initial frame to choose database schema
    initial_frame = [
        [sg.Text('Choose your database schema')],
        [sg.InputCombo(('TPC-H', 'IMDB'), size=(20, 1), key='-SCHEMA-')],
        [sg.Button('Select Database', key='-SELECT_SCHEMA-')]
    ]

    # Frame to choose query
    frame_select_query = [
        [sg.Text('Current database schema')],
        [sg.Text(size=(12,1), key='-TEXT_SCHEMA-')],
        [sg.InputCombo(('Query1','Query2','Query3', 'Query4', 'Query5', 'Query6', 'Query7', 'Query8'), size=(20, 1), key='-QUERY-')],
        [sg.Button('Select Query', key='-SELECT_QUERY-'), sg.Button('Back', key='Back')]
    ]

    # Frame to show QEP description
    frame_display_QEP_description_1 = [
        [sg.Multiline(key='-TEXT_QEP_1-', size=(60, 18))]
    ]

    frame_display_QEP_description_2 = [
        [sg.Multiline(key='-TEXT_QEP_2-', size=(60, 18))]
    ]

    frame_display_QEP_description_3 = [
        [sg.Multiline(key='-TEXT_QEP_3-', size=(60, 18))]
    ]
    frame_display_AEP_description_1 = [
        [sg.Multiline(key='-TEXT_AEP_1-', size=(60, 18))]
    ]
    frame_display_AEP_description_2 = [
        [sg.Multiline(key='-TEXT_AEP_2-', size=(60, 18))]
    ]
    frame_display_AEP_description_3 = [
        [sg.Multiline(key='-TEXT_AEP_3-', size=(60, 18))]
    ]

    frame_display_visual_QEP = [
        [sg.Image(key='-IMAGE-', expand_x=True, expand_y=True)]
    ]

    # Frame to show Query chosen
    frame_display_query = [
        [sg.Text('Please input your SQL query')],
        [sg.Multiline(key='-TEXT_QUERY-', size=(60, 10), tooltip = '')],
        [sg.Button('Submit', tooltip='Submit your query')],
        [sg.Frame("Visualise Plan", frame_display_visual_QEP)],
        
    ]
    
    frame_display_QEP1 = [
       [sg.Frame("Difference between QEP and AEP 1", frame_display_AEP_description_1, expand_x=True, expand_y=True)],
       [sg.Button('1', key='1'), sg.Button('2', key='2'), sg.Button('3', key='3')],
       [sg.Frame("Natural Language Description of QEP", frame_display_QEP_description_1, expand_x=True, expand_y=True)]
    ]
    frame_display_QEP2 = [
         [sg.Frame("Difference between QEP and AEP 2", frame_display_AEP_description_2, expand_x=True, expand_y=True)],
         [sg.Button('1', key='1'), sg.Button('2', key='2'), sg.Button('3', key='3')],
         [sg.Frame("Natural Language Description of QEP", frame_display_QEP_description_2, expand_x=True, expand_y=True)]
     ]
    frame_display_QEP3 = [
        [sg.Frame("Difference between QEP and AEP 3", frame_display_AEP_description_3, expand_x=True, expand_y=True)],
        [sg.Button('1', key='1'), sg.Button('2', key='2'), sg.Button('3', key='3')],
        [sg.Frame("Natural Language Description of QEP", frame_display_QEP_description_3, expand_x=True, expand_y=True)]
    ]
    
    # Layout to combine all frames
    layout = [
    [sg.Frame('Choose your database schema', initial_frame, size=(WIDTH,HEIGHT), visible=True, key='-COL1-'),
     sg.Frame('Database Schema', frame_select_query, size=(200,HEIGHT), visible=False, key='-COL2-'),
     sg.Frame('User Query', frame_display_query, size=(500,HEIGHT), visible=False, key='-COL3-'),
     sg.Frame('AEP AND QEP', frame_display_QEP1, size=(WIDTH,HEIGHT), visible=False, key='-COL4-'),
     sg.Frame('AEP AND QEP', frame_display_QEP2, size=(WIDTH,HEIGHT), visible=False, key='-COL5-'),
     sg.Frame('AEP AND QEP', frame_display_QEP3, size=(WIDTH,HEIGHT), visible=False, key='-COL6-'),
     sg.Text('', size=50, key='STATUS', visible=False)]
    ]

    margins = (2, 2)
    return sg.Window('CZ4031 Project 2', layout, margins = margins, finalize=True, resizable=True)

# Main function
def interface(host,database,user,password):
    window = build()
    pop_win = None
    db = Database(host,database,user,password)
    AEP_list = []
    # Query dictionary to store query
    query_dict = {
    'Query1': '''select 
    l_returnflag,
    l_linestatus,
    sum(l_quantity) as sum_qty,
    sum(l_extendedprice) as sum_base_price,
    sum(l_extendedprice * (1 - l_discount)) as sum_disc_price,
    sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge,
    avg(l_quantity) as avg_qty,
    avg(l_extendedprice) as avg_price,
    avg(l_discount) as avg_disc,
    count(*) as count_order
from
    lineitem
where
    l_extendedprice > 100
    group by
    l_returnflag,
    l_linestatus
order by
    l_returnflag,
    l_linestatus;
    ''', 

    'Query2': '''select
    l_orderkey,
    sum(l_extendedprice * (1 - l_discount)) as revenue,
    o_orderdate,
    o_shippriority
from
    customer,
    orders,
    lineitem
where
    c_mktsegment = 'BUILDING'
    and c_custkey = o_custkey
    and l_orderkey = o_orderkey
    and o_totalprice > 10
    and l_extendedprice > 10
group by
    l_orderkey,
    o_orderdate,
    o_shippriority
order by
    revenue desc,
    o_orderdate;
    ''', 

    'Query3': '''select
    o_orderpriority,
    count(*) as order_count
from
    orders
where
    o_totalprice > 100
and exists (
    select
        *
    from
        lineitem
    where
        l_orderkey = o_orderkey
        and l_extendedprice > 100
)
group by
    o_orderpriority
order by
    o_orderpriority;
    ''',

    'Query4' : '''select
      n_name,
      sum(l_extendedprice * (1 - l_discount)) as revenue
from
    customer,
    orders,
    lineitem,
    supplier,
    nation,
    region
where
    c_custkey = o_custkey
    and l_orderkey = o_orderkey
    and l_suppkey = s_suppkey
    and c_nationkey = s_nationkey
    and s_nationkey = n_nationkey
    and n_regionkey = r_regionkey
    and r_name = 'ASIA'
    and o_orderdate >= '1994-01-01'
    and o_orderdate < '1995-01-01'
    and c_acctbal > 10
    and s_acctbal > 20
group by
    n_name
order by
    revenue desc;
      ''',

      'Query5': '''select
      sum(l_extendedprice * l_discount) as revenue
from
    lineitem
where
    l_extendedprice > 100;
    ''',

    'Query6':'''select
      supp_nation,
      cust_nation,
      l_year,
      sum(volume) as revenue
from
    (
    select
        n1.n_name as supp_nation,
        n2.n_name as cust_nation,
        DATE_PART('YEAR',l_shipdate) as l_year,
        l_extendedprice * (1 - l_discount) as volume
    from
        supplier,
        lineitem,
        orders,
        customer,
        nation n1,
        nation n2
    where
        s_suppkey = l_suppkey
        and o_orderkey = l_orderkey
        and c_custkey = o_custkey
        and s_nationkey = n1.n_nationkey
        and c_nationkey = n2.n_nationkey
        and (
        (n1.n_name = 'FRANCE' and n2.n_name = 'GERMANY')
        or (n1.n_name = 'GERMANY' and n2.n_name = 'FRANCE')
        )
        and l_shipdate between '1995-01-01' and '1996-12-31'
        and o_totalprice > 100
        and c_acctbal > 10
    ) as shipping
group by
    supp_nation,
    cust_nation,
    l_year
order by
    supp_nation,
    cust_nation,
    l_year;
    ''',

    'Query7': '''select
      o_year,
      sum(case
        when nation = 'BRAZIL' then volume
        else 0
      end) / sum(volume) as mkt_share
from
    (
    select
        DATE_PART('YEAR',o_orderdate) as o_year,
        l_extendedprice * (1 - l_discount) as volume,
        n2.n_name as nation
    from
        part,
        supplier,
        lineitem,
        orders,
        customer,
        nation n1,
        nation n2,
        region
    where
        p_partkey = l_partkey
        and s_suppkey = l_suppkey
        and l_orderkey = o_orderkey
        and o_custkey = c_custkey
        and c_nationkey = n1.n_nationkey
        and n1.n_regionkey = r_regionkey
        and r_name = 'AMERICA'
        and s_nationkey = n2.n_nationkey
        and o_orderdate between '1995-01-01' and '1996-12-31'
        and p_type = 'ECONOMY ANODIZED STEEL'
        and s_acctbal > 10
        and l_extendedprice > 100
    ) as all_nations
group by
    o_year
order by
    o_year;
    ''',
      'Query8': '''select
      n_name,
      o_year,
      sum(amount) as sum_profit
from
    (
    select
        n_name,
        DATE_PART('YEAR',o_orderdate) as o_year,
        l_extendedprice * (1 - l_discount) - ps_supplycost * l_quantity as amount
    from
        part,
        supplier,
        lineitem,
        partsupp,
        orders,
        nation
    where
        s_suppkey = l_suppkey
        and ps_suppkey = l_suppkey
        and ps_partkey = l_partkey
        and p_partkey = l_partkey
        and o_orderkey = l_orderkey
        and s_nationkey = n_nationkey
        and p_name like '%green%'
        and s_acctbal > 10
        and ps_supplycost > 100
    ) as profit
group by
    n_name,
    o_year
order by
    n_name,
    o_year desc;
    '''}

    # List of planner method configurations to disable and enable
    set_seq_off = 'SET enable_seqscan to off;'
    set_seq_on = 'SET enable_seqscan to on;'
    set_index_scan_off = 'SET enable_indexscan to off;'
    set_index_scan_on = 'SET enable_indexscan to on;'
    set_hash_join_off = 'SET enable_hashjoin to off;'
    set_hash_join_on = 'SET enable_hashjoin to on;'
    set_merge_join_off = 'SET enable_mergejoin to off;'
    set_merge_join_on = 'SET enable_mergejoin to on;'
    set_sort_off = 'SET enable_sort to off;'
    set_sort_on = 'SET enable_sort to on;'
    set_gather_merge_off = 'SET enable_gathermerge to off;'
    set_gather_merge_on = 'SET enable_gathermerge to on;'
    set_nested_loop_off = 'SET enable_nestloop to off;'
    set_nested_loop_on = 'SET enable_nestloop to on;'
    set_bitmap_scan_off = 'SET enable_bitmapscan to off;'
    set_bitmap_scan_on = 'SET enable_bitmapscan to on;'

    dummy_text = 'dummy text'
    count = 0
    aep_node_type_list = []
    aep_node_cost_list = []
    aep_object_list = []
    result_diff = []
    # Display window
    while True:
        event, values = window.read()
        print(event)
        # End program if user closes window or clicks cancel
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        # Go back to database schema selection window
        if event == 'Back':
            window['-COL1-'].update(visible=True)
            window['-COL2-'].update(visible=False)
            window['-COL3-'].update(visible=False)
            window['-COL4-'].update(visible=False)
            window['-TEXT_QUERY-'].update('')
            window['-IMAGE-'].update('')
            window['-TEXT_QEP-'].update('')

        # If user selects a database schema, then show the corresponding frames 
        if event == '-SELECT_SCHEMA-' and values['-SCHEMA-'] != '':
            window['-COL1-'].update(visible=False)
            window['-COL2-'].update(visible=True)
            window['-COL3-'].update(visible=True)
            window['-COL4-'].update(visible=True)
            window['-TEXT_SCHEMA-'].update(values['-SCHEMA-'])
        
        # If user selects a query, then show the corresponding query in display_query frame
        if event == '-SELECT_QUERY-' and values['-QUERY-'] != '':
            window['-TEXT_QUERY-'].update(query_dict[values['-QUERY-']])

        if event[0] == '1':
            window['-COL4-'].update(visible=True)
            window['-COL5-'].update(visible=False)
            window['-COL6-'].update(visible=False)
        
        if event[0] == '2':
            window['-COL4-'].update(visible=False)
            window['-COL5-'].update(visible=True)
            window['-COL6-'].update(visible=False)
        
        if event[0] == '3':
            window['-COL4-'].update(visible=False)
            window['-COL5-'].update(visible=False)
            window['-COL6-'].update(visible=True)

        if event == 'EXECUTION DONE':
            popup_win.close()
            popup_win = None
        # Move window to center of screen
        move_center(window)

        # Schema chosen by user
        schema = values['-SCHEMA-']

        # Query chosen by user
        # print('text_query: ', values['-TEXT_QUERY-'])
        # print('query: ', values['-QUERY-'])

        # Query to be executed in PostgreSQL
        # IMPORTANT
        query = values['-TEXT_QUERY-']
        query = 'EXPLAIN(ANALYZE, FORMAT JSON) ' + query
        
        
        def get_QEP_and_AEP(query):
            count = 0
            qep = db.get_query_result(query)
            if qep == None:
                return None
            print(qep)
            qep_obj = json.loads(json.dumps(qep))
            parse_json_obj = parse_json(qep_obj)

            # Get the distinct node types in the QEP
            qep_node_type_list = parse_json_obj[1]

            # Get the cost of each node type in the QEP
            qep_node_cost_list = parse_json_obj[2]
            print(qep_node_type_list)
            qep_nlp = get_description(qep_obj)
            qep_tree = get_tree(qep_obj)
            qep_nlp += '\n\n' + qep_tree
            print(qep_node_cost_list)
            for node in set(qep_node_type_list):
                # For now, max number of AEP is 3
                if count == 4:
                    break
                if node == 'Seq Scan':
                    # FIRST AEP
                    db.execute_query(set_seq_off)

                    result_AEP_seq = db.get_query_result(query)
                    print(result_AEP_seq)
                    result_AEP_seq_obj = json.loads(json.dumps(result_AEP_seq))
                    parse_json_obj = parse_json(result_AEP_seq_obj)

                    # Get the distinct node types in the AEP
                    aep_node_type_list.append(parse_json_obj[1])

                    # Get the cost of each node type in the AEP
                    aep_node_cost_list.append(parse_json_obj[2])

                    result_AEP_seq_nlp = get_description(result_AEP_seq_obj)
                    total_cost = get_total_cost(result_AEP_seq_obj)
                    print(total_cost)
                    result_AEP_seq_tree = get_tree(result_AEP_seq_obj)
                    result_AEP_seq_nlp += '\n\n' + result_AEP_seq_tree + '\n\n' + 'With Sequential Scan Turned Off'
                    db.execute_query(set_seq_on)
                    #AEP_list.append(result_AEP_seq_nlp)
                    aep_object_list.append(result_AEP_seq_obj)


                elif node == 'Sort':
                    set_sort_off = 'SET enable_sort to off;'
                    db.execute_query(set_sort_off)
                    result_AEP_sort = db.get_query_result(query)
                    print(result_AEP_sort)
                    result_AEP_sort_obj = json.loads(json.dumps(result_AEP_sort))
                    parse_json_obj = parse_json(result_AEP_sort_obj)

                    # Get the distinct node types in the AEP
                    aep_node_type_list.append(parse_json_obj[1])

                    # Get the cost of each node type in the AEP
                    aep_node_cost_list.append(parse_json_obj[2])

                    result_AEP_sort_nlp = get_description(result_AEP_sort_obj)
                    total_cost = get_total_cost(result_AEP_sort_obj)
                    print(total_cost)
                    result_AEP_sort_tree = get_tree(result_AEP_sort_obj)
                    result_AEP_sort_nlp += '\n\n' + result_AEP_sort_tree + '\n\n' + 'With Sort Turned Off'
                    set_sort_on = 'SET enable_sort to on;'
                    db.execute_query(set_sort_on)
                    #AEP_list.append(result_AEP_sort_nlp)
                    aep_object_list.append(result_AEP_sort_obj)
                
                elif node == 'Gather Merge':
                    db.execute_query(set_gather_merge_off)
                    result_AEP_gather = db.get_query_result(query)
                    print(result_AEP_gather)
                    result_AEP_gather_obj = json.loads(json.dumps(result_AEP_gather))
                    parse_json_obj = parse_json(result_AEP_gather_obj)

                    # Get the distinct node types in the AEP
                    aep_node_type_list.append(parse_json_obj[1])

                    # Get the cost of each node type in the AEP
                    aep_node_cost_list.append(parse_json_obj[2])

                    result_AEP_gather_nlp = get_description(result_AEP_gather_obj)
                    total_cost = get_total_cost(result_AEP_gather_obj)
                    print(total_cost)
                    result_AEP_gather_tree = get_tree(result_AEP_gather_obj)
                    result_AEP_gather_nlp += '\n\n' + result_AEP_gather_tree + '\n\n' + 'With Gather Merge Turned Off'
                    db.execute_query(set_gather_merge_on)
                    #AEP_list.append(result_AEP_gather_nlp)
                    aep_object_list.append(result_AEP_gather_obj)
                
                elif node == 'Hash Join':
                    db.execute_query(set_hash_join_off)
                    result_AEP_hash = db.get_query_result(query)
                    print(result_AEP_hash)
                    result_AEP_hash_obj = json.loads(json.dumps(result_AEP_hash))
                    parse_json_obj = parse_json(result_AEP_hash_obj)

                    # Get the distinct node types in the AEP
                    aep_node_type_list.append(parse_json_obj[1])

                    # Get the cost of each node type in the AEP
                    aep_node_cost_list.append(parse_json_obj[2])

                    result_AEP_hash_nlp = get_description(result_AEP_hash_obj)
                    total_cost = get_total_cost(result_AEP_hash_obj)
                    print(total_cost)
                    result_AEP_hash_tree = get_tree(result_AEP_hash_obj)
                    result_AEP_hash_nlp += '\n\n' + result_AEP_hash_tree + '\n\n' + 'With Hash Join Turned Off'
                    db.execute_query(set_hash_join_on)
                    #AEP_list.append(result_AEP_hash_nlp)
                    aep_object_list.append(result_AEP_hash_obj)
                
                elif node == 'Nested Loop':
                    db.execute_query(set_nested_loop_off)
                    result_AEP_nested = db.get_query_result(query)
                    print(result_AEP_nested)
                    result_AEP_nested_obj = json.loads(json.dumps(result_AEP_nested))
                    parse_json_obj = parse_json(result_AEP_nested_obj)

                    # Get the distinct node types in the AEP
                    aep_node_type_list.append(parse_json_obj[1])

                    # Get the cost of each node type in the AEP
                    aep_node_cost_list.append(parse_json_obj[2])

                    result_AEP_nested_nlp = get_description(result_AEP_nested_obj)
                    total_cost = get_total_cost(result_AEP_nested_obj)
                    print(total_cost)
                    result_AEP_nested_tree = get_tree(result_AEP_nested_obj)
                    result_AEP_nested_nlp += '\n\n' + result_AEP_nested_tree + '\n\n' + 'With Nested Loop Turned Off'
                    db.execute_query(set_nested_loop_on)
                    #AEP_list.append(result_AEP_nested_nlp)
                    aep_object_list.append(result_AEP_nested_obj)

                elif node == 'Bitmap Heap Scan':
                    db.execute_query(set_bitmap_scan_off)
                    result_AEP_bitmap = db.get_query_result(query)
                    print(result_AEP_bitmap)
                    result_AEP_bitmap_obj = json.loads(json.dumps(result_AEP_bitmap))
                    parse_json_obj = parse_json(result_AEP_bitmap_obj)

                    # Get the distinct node types in the AEP
                    aep_node_type_list.append(parse_json_obj[1])

                    # Get the cost of each node type in the AEP
                    aep_node_cost_list.append(parse_json_obj[2])

                    result_AEP_bitmap_nlp = get_description(result_AEP_bitmap_obj)
                    total_cost = get_total_cost(result_AEP_bitmap_obj)
                    print(total_cost)
                    result_AEP_bitmap_tree = get_tree(result_AEP_bitmap_obj)
                    result_AEP_bitmap_nlp += '\n\n' + result_AEP_bitmap_tree + '\n\n' + 'With Bitmap Heap Scan Turned Off'
                    db.execute_query(set_bitmap_scan_on)
                    #AEP_list.append(result_AEP_bitmap_nlp)
                    aep_object_list.append(result_AEP_bitmap_obj)
                
                elif node == 'Index Scan':
                    db.execute_query(set_index_scan_off)
                    result_AEP_index = db.get_query_result(query)
                    print(result_AEP_index)
                    result_AEP_index_obj = json.loads(json.dumps(result_AEP_index))
                    parse_json_obj = parse_json(result_AEP_index_obj)

                    # Get the distinct node types in the AEP
                    aep_node_type_list.append(parse_json_obj[1])

                    # Get the cost of each node type in the AEP
                    aep_node_cost_list.append(parse_json_obj[2])

                    result_AEP_index_nlp = get_description(result_AEP_index_obj)
                    total_cost = get_total_cost(result_AEP_index_obj)
                    print(total_cost)
                    result_AEP_index_tree = get_tree(result_AEP_index_obj)
                    result_AEP_index_nlp += '\n\n' + result_AEP_index_tree + '\n\n' + 'With Index Scan Turned Off'
                    db.execute_query(set_index_scan_on)
                    #AEP_list.append(result_AEP_index_nlp)
                    aep_object_list.append(result_AEP_index_obj)
                
                count += 1

            # indices = [i for i, x in enumerate(query) if x == "="]
            # print(indices)
            # for index in indices:
            #     print(query[index-5:index+5].replace(" ", "").replace("=", "").replace("_",""))
            #     if (query[index-5:index+5].replace(" ", "").replace("=", "").replace("_","")).isalpha():
            #         set_hash_join_off = 'SET enable_hashjoin to off;'
            #         db.execute_query(set_hash_join_off)

            #         result_AEP_hash = db.get_query_result(query)
            #         print(result_AEP_hash)
            #         result_AEP_hash_obj = json.loads(json.dumps(result_AEP_hash))
            #         result_AEP_hash_nlp = get_description(result_AEP_hash_obj)
            #         total_cost = get_total_cost(result_AEP_hash_obj)
            #         print(total_cost)
            #         result_AEP_hash_tree = get_tree(result_AEP_hash_obj)
            #         result_AEP_hash_nlp += '\n\n' + result_AEP_hash_tree + '\n\n' + 'With Hash Join Turned Off'
            #         set_hash_join_on = 'SET enable_hashjoin to on;'
            #         db.execute_query(set_hash_join_on)
            #         AEP_list.append(result_AEP_hash_nlp)
            #         break
            #print(AEP_list[0])
            print(AEP_list)
            print(aep_node_type_list)
            print(aep_node_cost_list)
            # for i in range(len(AEP_list)):
            #     window[f'-TEXT_AEP_{i+1}-'].update(AEP_list[i])

            for object in aep_object_list:
                result_diff.append(get_diff(qep_obj, object))
            
            print(result_diff)
            for i in range(len(result_diff)):
                window[f'-TEXT_AEP_{i+1}-'].update(result_diff[i])

            AEP_list.clear()
            aep_object_list.clear()
            result_diff.clear()
            aep_node_type_list.clear()
            aep_node_cost_list.clear()
            count = 0
            window['-TEXT_QEP_1-'].update(qep_nlp)
            window['-TEXT_QEP_2-'].update(qep_nlp)
            window['-TEXT_QEP_3-'].update(qep_nlp)

            window.write_event_value('EXECUTION DONE', None)

        # If user clicks on the execute button, then execute the query 
        # and enable/disable planner options based on QEP
        if event == 'Submit':
            print(query)
            # TODO: implement PostsgreSQL implementation, run query and get QEP
            image = resize_image('test.png', WIDTH, HEIGHT//2)
            image = ImageTk.PhotoImage(image=image)
            window['-IMAGE-'].update(data=image)
            #window['-TEXT_QEP_1-'].update(QEP_description_holder)
            window['-TEXT_QUERY-'].set_tooltip(dummy_text)
            popup_win = popup('Please wait while the query is being executed...')
            window.force_focus()
            
            # CHOSEN QEP
            threading.Thread(target= get_QEP_and_AEP, args=(query,)).start()

        # print(schema)
    window.close()



def get_description(json_obj):
    descriptions = get_text(json_obj)
    result = ""
    for description in descriptions:
        result = result + description + "\n"
    return result

def get_tree(json_obj):
    head = parse_json(json_obj)[0]
    return generate_tree("", head)

def get_difference(json_object_A, json_object_B):
        diff = get_diff(json_object_A, json_object_B)
        return diff