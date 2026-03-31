# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
from snowflake.snowpark import Session

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!"""
)

# Add a name box
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# session = get_active_session()

def create_session():
    connection_parameters = st.secrets["snowflake"]
    return Session.builder.configs(connection_parameters).create()

session = create_session()

# my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
my_dataframe = session.table("smoothies.public.fruit_options") \
                      .select(col("FRUIT_NAME"), col("SEARCH_ON"))

# st.dataframe(data=my_dataframe, use_container_width=True)

fruit_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_df["FRUIT_NAME"].tolist()
)

if ingredients_list:
    ingredients_string = ''

    # for fruit_chosen in ingredients_list:
    #     ingredients_string += fruit_chosen + ' '
    #     # Use Our fruit_chosen Variable in the API Call
    #     st.subheader(fruit_chosen + 'Nutrition Information')

    #     # SmoothieFroot API call for each fruit
    #     url = f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}"
    #     smoothiefroot_response = requests.get(url)

    #     st.dataframe(
    #         data=smoothiefroot_response.json(),
    #         use_container_width=True
    #     )
    for fruit_chosen in ingredients_list:
        search_term = (
            my_dataframe
            .filter(col("FRUIT_NAME") == fruit_chosen)
            .select(col("SEARCH_ON"))
            .collect()[0][0]
        )
    
        url = f"https://my.smoothiefroot.com/api/fruit/{search_term}"
        response = requests.get(url)
    
        st.dataframe(response.json(), use_container_width=True)

    my_insert_stmt = f"""
        insert into smoothies.public.orders(ingredients, name_on_order)
        values ('{ingredients_string}', '{name_on_order}')
    """

    st.write(my_insert_stmt)

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")

# smoothiefroot_response = requests.get(
#     "https://my.smoothiefroot.com/api/fruit/watermelon"
# )

# st.json(smoothiefroot_response.json())

# sf_df = st.dataframe(
#     data=smoothiefroot_response.json(),
#     use_container_width=True
# )
