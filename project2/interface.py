from winreg import QueryInfoKey
import PySimpleGUI as sg
from preprocessing import *
from annotation import *
import threading

# Add a touch of color
sg.theme('DarkBlue3')   

# Change font and font size
sg.set_options(font=('Helvetica', 12))
sg.set_options(tooltip_font=('Helvetica', 11))
# Default size for frames, can be changed
WIDTH, HEIGHT = sg.Window.get_screen_size()
# WIDTH = 500
# HEIGHT = 700

query = ''

# Blank frame for testing purposes
def blank_frame():
    return sg.Frame("", [[]], pad=(5, 3), expand_x=True, expand_y=True, background_color='#404040', border_width=0)

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

# Connect to the database via the credentials in config.json
def connect_to_db():
    try:
        config = get_json()
        db_config = config['db']
        db = Database(db_config['host'], db_config['port'],db_config['database'], db_config['user'], db_config['password'])
        return db
    except Exception as e:
        print(e)
        return None

# Build the GUI
def build():
    
    button_1 = sg.Button('Node1', key='-NODE_1-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node1', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_2 = sg.Button('Node2', key='-NODE_2-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node2', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_3 = sg.Button('Node3', key='-NODE_3-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node3', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_4 = sg.Button('Node4', key='-NODE_4-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node4', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_5 = sg.Button('Node5', key='-NODE_5-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node5', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_6 = sg.Button('Node6', key='-NODE_6-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node6', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_7 = sg.Button('Node7', key='-NODE_7-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node7', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_8 = sg.Button('Node8', key='-NODE_8-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node8', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_9 = sg.Button('Node9', key='-NODE_9-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node9', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_10 = sg.Button('Node10', key='-NODE_10-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node10', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_11 = sg.Button('Node11', key='-NODE_11-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node11', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_12 = sg.Button('Node12', key='-NODE_12-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node12', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_13 = sg.Button('Node13', key='-NODE_13-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node13', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_14 = sg.Button('Node14', key='-NODE_14-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node14', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_15 = sg.Button('Node15', key='-NODE_15-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node15', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_16 = sg.Button('Node16', key='-NODE_16-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node16', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_17 = sg.Button('Node17', key='-NODE_17-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node17', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_18 = sg.Button('Node18', key='-NODE_18-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node18', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_19 = sg.Button('Node19', key='-NODE_19-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node19', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_20 = sg.Button('Node20', key='-NODE_20-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node20', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_21 = sg.Button('Node21', key='-NODE_21-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node21', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_22 = sg.Button('Node22', key='-NODE_22-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node22', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_23 = sg.Button('Node23', key='-NODE_23-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node23', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_24 = sg.Button('Node24', key='-NODE_24-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node24', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_25 = sg.Button('Node25', key='-NODE_25-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node25', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_26 = sg.Button('Node26', key='-NODE_26-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node26', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_27 = sg.Button('Node27', key='-NODE_27-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node27', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_28 = sg.Button('Node28', key='-NODE_28-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node28', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_29 = sg.Button('Node29', key='-NODE_29-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node29', visible=False, disabled=True, disabled_button_color=('white', '#404040'))
    button_30 = sg.Button('Node30', key='-NODE_30-', size=(10, 1), pad=(10, 10), button_color=('white', '#404040'), tooltip='Node30', visible=False, disabled=True, disabled_button_color=('white', '#404040'))

    arrow_1 = sg.Button('↑', key='-ARROW_1-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_2 = sg.Button('↑', key='-ARROW_2-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_3 = sg.Button('↑', key='-ARROW_3-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_4 = sg.Button('↑', key='-ARROW_4-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_5 = sg.Button('↑', key='-ARROW_5-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_6 = sg.Button('↑', key='-ARROW_6-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_7 = sg.Button('↑', key='-ARROW_7-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_8 = sg.Button('↑', key='-ARROW_8-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_9 = sg.Button('↑', key='-ARROW_9-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_10 = sg.Button('↑', key='-ARROW_10-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_11 = sg.Button('↑', key='-ARROW_11-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_12 = sg.Button('↑', key='-ARROW_12-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_13 = sg.Button('↑', key='-ARROW_13-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_14 = sg.Button('↑', key='-ARROW_14-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_15 = sg.Button('↑', key='-ARROW_15-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_16 = sg.Button('↑', key='-ARROW_16-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_17 = sg.Button('↑', key='-ARROW_17-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_18 = sg.Button('↑', key='-ARROW_18-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_19 = sg.Button('↑', key='-ARROW_19-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_20 = sg.Button('↑', key='-ARROW_20-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_21 = sg.Button('↑', key='-ARROW_21-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_22 = sg.Button('↑', key='-ARROW_22-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_23 = sg.Button('↑', key='-ARROW_23-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_24 = sg.Button('↑', key='-ARROW_24-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_25 = sg.Button('↑', key='-ARROW_25-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_26 = sg.Button('↑', key='-ARROW_26-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_27 = sg.Button('↑', key='-ARROW_27-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_28 = sg.Button('↑', key='-ARROW_28-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)
    arrow_29 = sg.Button('↑', key='-ARROW_29-', size=(2, 1), pad=(20, 10), button_color=('black','white'), visible=False, disabled=True)

    button_column = sg.Column([
                [button_30], [arrow_29], [button_29], [arrow_28], [button_28], [arrow_27], [button_27], [arrow_26], [button_26], [arrow_25], 
                [button_25], [arrow_24], [button_24], [arrow_23], [button_23], [arrow_22], [button_22], [arrow_21], [button_21], [arrow_20], 
                [button_20], [arrow_19], [button_19], [arrow_18], [button_18], [arrow_17], [button_17], [arrow_16], [button_16], [arrow_15], 
                [button_15], [arrow_14], [button_14], [arrow_13], [button_13], [arrow_12], [button_12], [arrow_11], [button_11], [arrow_10],
                [button_10], [arrow_9], [button_9], [arrow_8], [button_8], [arrow_7], [button_7], [arrow_6], [button_6], [arrow_5],
                [button_5], [arrow_4], [button_4], [arrow_3], [button_3], [arrow_2], [button_2], [arrow_1], [button_1]],
                pad=(0, 0), expand_x=True, expand_y=True, element_justification='center', vertical_alignment='top', scrollable=True, vertical_scroll_only=True, size=(500, 500), key='-BUTTON_COLUMN-')
    
    # Initial frame to choose database schema
    initial_frame = [
        [sg.InputCombo(('TPC-H', 'IMDB'), size=(20, 1), key='-SCHEMA-')],
        [sg.Button('Select Database', key='-SELECT_SCHEMA-')]
    ]

    # Frame to display NLP QEP description
    frame_display_QEP_description = [
        [sg.Multiline(key='-TEXT_QEP-', size=(60, 18))]
    ]

    # Frame to choose query
    frame_select_query = [
        [sg.Text('Current database schema')],
        [sg.Text(size=(12,1), key='-TEXT_SCHEMA-')],
        [sg.InputCombo(('Query1','Query2','Query3', 'Query4', 'Query5', 'Query6', 'Query7', 'Query8'), size=(20, 1), key='-QUERY-')],
        [sg.Button('Select Query', key='-SELECT_QUERY-')],
        [sg.Text('Please input your SQL query')],
        [sg.Multiline(key='-TEXT_QUERY-', size=(60, 10))],
        [sg.Button('Submit', tooltip='Submit your query')],
        [sg.Frame("QEP Step-By-Step NLP:", frame_display_QEP_description)]
    ]

    # Frame to display visualise plan
    frame_display_visual_QEP = [
        [button_column]    
    ]


    # Layout to combine all frames
    layout = [
    [
     sg.Frame('Choose your database schema', initial_frame, size=(WIDTH,HEIGHT), visible=True, key='-COL1-'),
     sg.Frame('Database Schema', frame_select_query, size=(500,HEIGHT), visible=False, key='-COL2-'),
     sg.Frame('QEP Visualise Plan', frame_display_visual_QEP, size=(WIDTH,HEIGHT), visible=False, key='-COL3-'),
     sg.Text('', size=50, key='STATUS', visible=False)]
    ]

    margins = (2, 2)
    return sg.Window('CZ4031 Project 2', layout, margins = margins, finalize=True, resizable=True)

# Main function to run the GUI
def interface():
    # Create the window
    window = build()
    popup_win = None

    # Connect to the database
    db = connect_to_db()

    # List to store the AQPs
    AQP_list = []
    
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

    # List of AQP node types
    aqp_node_type_list = []

    # List of total cost of each AQP
    aqp_node_cost_list = []

    # List of AQP json format output
    aqp_object_list = []
    # Display window
    while True:
        event, values = window.read()
        # End program if user closes window or clicks cancel
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        
        # If user selects a database schema, then show the corresponding frames 
        if event == '-SELECT_SCHEMA-' and values['-SCHEMA-'] != '':
            window['-COL1-'].update(visible=False)
            window['-COL2-'].update(visible=True)
            window['-COL3-'].update(visible=True)
            window['-TEXT_SCHEMA-'].update(values['-SCHEMA-'])
        
        # If user selects a query, then show the corresponding query in display_query frame
        if event == '-SELECT_QUERY-' and values['-QUERY-'] != '':
            window['-TEXT_QUERY-'].update(query_dict[values['-QUERY-']])


        # Close the popup window after query is completed
        if event == 'EXECUTION DONE':
            popup_win.close()
            popup_win = None


        # Query to be executed in PostgreSQL
        # IMPORTANT
        query = values['-TEXT_QUERY-']
        query = 'EXPLAIN (COSTS, VERBOSE, BUFFERS, FORMAT JSON) ' + query
        
       # If user clicks on the execute button, then execute the query 
        # and enable/disable planner options based on QEP
        if event == 'Submit':
            if query == 'EXPLAIN (COSTS, VERBOSE, BUFFERS, FORMAT JSON) ':
                continue

            popup_win = popup('Please wait while the query is being executed...')
            window.force_focus()
            
            # Parallel thread to execute the query on top of the pop up loading
            threading.Thread(target= get_QEP_and_AEP, args=(query,)).start()

        # Execute the query to get the QEP and AQP
        def get_QEP_and_AEP(query):
            
            # Reset the visualization frame and QEP NLP Description frame on every query execution
            reset_visualisation()
            try:
                qep = db.get_query_result(query)
            
            except Exception as e:
                return
            if qep == None:
                return None
            
            # Parse json format query plan to parse_json
            parse_json_obj = parse_json(qep)

            # Get the distinct node types in the QEP
            qep_node_type_list = parse_json_obj[1]

            # Get the total cost of QEP
            qep_total_cost = parse_json_obj[2]

            # Get the NLP description of QEP
            qep_nlp = get_description(qep)

            # Disable planner methods based on QEP
            planner_method_off(qep_node_type_list)


            # AQP query to be executed in PostgreSQL based on disabled planner methods
            aqp = db.get_query_result(query)

            # Parse json format query plan to parse_json
            parse_json_obj = parse_json(aqp)

            # Get the distinct node types in the AQP
            aqp_node_type_list.append(parse_json_obj[1])

            # Get the total cost of AQP
            aqp_node_cost_list.append(parse_json_obj[2])

            # Append json format query plan to aqp_object_list
            aqp_object_list.append(aqp)

            # Reset planner method configurations to default
            planner_method_on()
            # Generate reasons for how each node is chosen in QEP as compared to AQP
            for i in range(len(aqp_object_list)):
                reasons, QEP_nodes = get_reason(qep, aqp_object_list[i], qep_total_cost, aqp_node_cost_list[i])

            # Draw the visualization plan
            visualise_plan(qep_nlp, reasons, QEP_nodes)

            # Reset the aqp_object_list, aqp_node_cost_list and aqp_node_type_list for next query execution
            AQP_list.clear()
            aqp_object_list.clear()
            aqp_node_type_list.clear()
            aqp_node_cost_list.clear()
            reasons.clear()

            # Notify pop up window that query execution is complete
            window.write_event_value('EXECUTION DONE', None)

         # Reset the visualization frame and QEP NLP Description frame
        def reset_visualisation():
            window['-TEXT_QEP-' ].update('')
            for i in range(1,31):
                window[f'-NODE_{i}-'].update(visible=False)
                window[f'-NODE_{i}-'].update('')
            
            for i in range(1,30):
                window[f'-ARROW_{i}-'].update(visible=False)
        
        # Draw the visualization plan
        def visualise_plan(qep_nlp, reasons, QEP_nodes):
            window['-TEXT_QEP-'].update(qep_nlp)
            QEP_nodes.reverse()
            reasons.reverse()

            # Draw the nodes corresponding to the QEP nodes
            for i in range(len(QEP_nodes)):
                    if QEP_nodes[i].node_type == 'Index Scan' and QEP_nodes[i].index_cond:
                        window[f'-NODE_{30-i}-'].update('Nested Loop')
                        window[f'-NODE_{30-i}-'].update(visible=True)
                        window[f'-NODE_{30-i}-'].set_tooltip(reasons[i])
                    
                    else:
                        window[f'-NODE_{30-i}-'].update(QEP_nodes[i].node_type)
                        window[f'-NODE_{30-i}-'].update(visible=True)
                        window[f'-NODE_{30-i}-'].set_tooltip(reasons[i])
 
            # Draw the arrows corresponding to the QEP nodes
            for i in range(len(QEP_nodes)-1):
                window[f'-ARROW_{29-i}-'].update(visible=True)
                
            window.refresh()
            window['-BUTTON_COLUMN-'].contents_changed()
        
        # Planner method configurations to be disabled based on QEP returned
        def planner_method_off(qep_node_type_list):
            for node in set(qep_node_type_list):
                if node == 'Seq Scan':
                    db.execute_query(set_seq_off)
                
                if node == 'Index Scan':
                    db.execute_query(set_index_scan_off)
                
                if node == 'Hash Join':
                    db.execute_query(set_hash_join_off)
                
                if node == 'Merge Join':
                    db.execute_query(set_merge_join_off)
                
                if node == 'Sort':
                    db.execute_query(set_sort_off)
                
                if node == 'Gather Merge':
                    db.execute_query(set_gather_merge_off)
                
                if node == 'Nested Loop':
                    db.execute_query(set_nested_loop_off)
                
                if node == 'Bitmap Heap Scan':
                    db.execute_query(set_bitmap_scan_off)
                
        # Reset planner method configurations to default
        def planner_method_on():
            db.execute_query(set_seq_on)
            db.execute_query(set_index_scan_on)
            db.execute_query(set_hash_join_on)
            db.execute_query(set_merge_join_on)
            db.execute_query(set_sort_on)
            db.execute_query(set_gather_merge_on)
            db.execute_query(set_nested_loop_on)
            db.execute_query(set_bitmap_scan_on)
    window.close()



# Get the description of the QEP
def get_description(json_obj):
    descriptions = get_text(json_obj)
    result = ""
    for description in descriptions:
        result = result + description + "\n\n"
    return result