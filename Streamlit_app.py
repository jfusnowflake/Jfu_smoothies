# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
# Write directly to the app
st.title(f"Customize Your Smoothie! :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)


name_on_order = st.text_input("Name on Smoothie:")
st.write("The name of your smoothie will be", name_on_order)


cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col("Fruit_Name"),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()


#Convert the snowpark dataframe to a pandas dataframe so we can use the loc function
pd_df = my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()


ingredients_list = st.multiselect(
    'Choos up  to 5 ingredients:'
    ,my_dataframe
    ,max_selections = 5
)   

if ingredients_list:
    
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
            ingredients_string += fruit_chosen + " "

            search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
            st.write('The search value for ',fruit_chosen,' is ', search_on, '.')

            st.subheader(fruit_chosen + ' Nutrition Information')
            smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
            #smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
            sf_df = st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)

    #st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    #st.write(my_insert_stmt)
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")

#new section to display smoothiefroot nutrition information
#st.text(smoothiefroot_response.json())
#disable it so that it wont display {'family': 'Cucurbitaceae', 'genus': 'Citrullus', 'id': 23, 'name': 'Watermelon', 'nutrition': {'carbs': 7.55, 'fat': 0.15, 'protein': 0.61, 'sugar': 6.2}, 'order': 'Cucurbitales'}
#put json into a dataframe


