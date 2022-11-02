from winreg import QueryInfoKey
import PySimpleGUI as sg
import time
from PIL import Image, ImageTk
from preprocessing import *

# Add a touch of color
sg.theme('DarkAmber')   

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
        [sg.Multiline(key='-TEXT_QUERY-', size=(60, 10))],
        [sg.Button('Submit')],
        [sg.Frame("Visualise Plan", frame_display_visual_QEP)],
        
    ]
    
    frame_display_QEP1 = [
       [sg.Frame("Natural Language Description of AEP 1", frame_display_AEP_description_1, expand_x=True, expand_y=True)],
       [sg.Button('1', key='1'), sg.Button('2', key='2'), sg.Button('3', key='3')],
       [sg.Frame("Natural Language Description of QEP", frame_display_QEP_description_1, expand_x=True, expand_y=True)]
    ]
    frame_display_QEP2 = [
         [sg.Frame("Natural Language Description of AEP 2", frame_display_AEP_description_2, expand_x=True, expand_y=True)],
         [sg.Button('1', key='1'), sg.Button('2', key='2'), sg.Button('3', key='3')],
         [sg.Frame("Natural Language Description of QEP", frame_display_QEP_description_2, expand_x=True, expand_y=True)]
     ]
    frame_display_QEP3 = [
        [sg.Frame("Natural Language Description of AEP 3", frame_display_AEP_description_3, expand_x=True, expand_y=True)],
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
     sg.Frame('AEP AND QEP', frame_display_QEP3, size=(WIDTH,HEIGHT), visible=False, key='-COL6-')]
    ]

    margins = (2, 2)
    return sg.Window('CZ4031 Project 2', layout, margins = margins, finalize=True, resizable=True)

# Main function
def interface(host,database,user,password):
    window = build()
    db = Database(host,database,user,password)
    number_of_AEP = 0
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

    # Temporary QEP description holder, to be replaced when implementation for QEP is done
    QEP_description_holder = '''The query is executed as follow.
Step 1, perform a sequential lineitem search and perform a table lineitem group aggregate with a l_returnflag and l_linestatus attribute grouping to get the T1 intermediate table .
Step 2, to obtain the final result , sort the table T1 with an attribute l_returnflag, l_linestatus .
    '''
    layout = 4
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
        print(query)

        # If user clicks on the execute button, then execute the query 
        # and show the image result in display_QEP frame and the description in display_QEP_description frame
        if event == 'Submit':
            # TODO: implement PostsgreSQL implementation, run query and get QEP
            image = resize_image('test.png', WIDTH, HEIGHT//2)
            image = ImageTk.PhotoImage(image=image)
            window['-IMAGE-'].update(data=image)
            #window['-TEXT_QEP_1-'].update(QEP_description_holder)

           

            
            
        
        # print(schema)
    window.close()


def get_description( json_obj):
    descriptions = get_text(json_obj)
    result = ""
    for description in descriptions:
        result = result + description + "\n"
    return result

def get_tree(json_obj):
    head = parse_json(json_obj)
    return generate_tree("", head)