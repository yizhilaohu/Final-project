from datetime import datetime
import datetime
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn')
import seaborn as sns

#################################################################################
# show the image
#################################################################################
# image = Image.open('hotel.jpeg')
# st.image(image, use_column_width=True)
#################################################################################
# show the title
#################################################################################
st.title('Hotel Bookings')
st.markdown(
    '''
    This app performs simple data searching and analysis of the booking and truly arriving data of the hotels
    - **Data source:** [Hotel Booking Demand](https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand)
    '''
)
datastill = pd.read_csv('hotel_bookings.csv')
data = pd.read_csv('hotel_bookings.csv')


#------------------处理数据合并年月日------------------------
# filter by date
# 1. deal with the data, to change the date time of the dataset into the form of 2015-07-12

# Converting string month to numerical one (Dec = 12, Jan = 1, etc.)

datetime_object = data['arrival_date_month'].str[0:3]
month_number = np.zeros(len(datetime_object))

# Creating a new column based on numerical representation of the months
for i in range(0, len(datetime_object)):
    datetime_object[i] = datetime.datetime.strptime(datetime_object[i], "%b")
    month_number[i] = datetime_object[i].month

# Float to integer conversion
month_number = pd.DataFrame(month_number).astype(int)

# 3 columns are merged into one
data['arrival_date'] = data['arrival_date_year'].map(str) + '-' + month_number[0].map(str) + '-' \
                       + data['arrival_date_day_of_month'].map(str)

# Dropping already used columns
data = data.drop(['arrival_date_year', 'arrival_date_month', 'arrival_date_day_of_month',
                  'arrival_date_week_number'], axis=1)

# Converting wrong datatype columns to correct type (object to datetime)
data['arrival_date'] = pd.to_datetime(data['arrival_date'])
data['reservation_status_date'] = pd.to_datetime(data['reservation_status_date'])

# Calculating total guests for each record
data['Total Guests'] = data['adults'] + data['children']

# Some data points include zero Total Guests, therefore I dropped them
data = data[data['Total Guests'] != 0]

# Total Number of Days Stayed
data['Total Stays'] = data['stays_in_weekend_nights'] + data['stays_in_week_nights']

dataNoCancel = data[data['is_canceled'] == 0]
dataNoCancel = dataNoCancel.reset_index(drop=True)

NumberOfGuests = dataNoCancel[['arrival_date', 'Total Guests']]

# Calculating Number of Guests Daily - Hotel
NumberOfGuests = dataNoCancel[['arrival_date', 'Total Guests']]
NumberOfGuests_Daily = dataNoCancel['Total Guests'].groupby(dataNoCancel['arrival_date']).sum()
NumberOfGuests_Daily = NumberOfGuests_Daily.resample('d').sum().to_frame()

#-------------------------选择展示问题-----------------------------
level_fliter = st.sidebar.radio(
    'Choose section',
    ('Dataset','Arrival','Daily rate','Customers')
    )

if level_fliter == 'Dataset':

    if st.checkbox('show dataset'):
        number = st.number_input('number of rows to view: ', 5, 1000)
        st.dataframe(data.sample(number))

    if st.button('variable names'):
        st.write(data.columns)

    if st.checkbox('shape of dataset'):
        st.write(data.shape)
    
    if st.checkbox('select columns to show'):
        allcol = data.columns.tolist()
        selectedcol = st.multiselect('select', allcol)
        new_df = data[selectedcol]
        st.dataframe(new_df)

elif level_fliter == 'Arrival':
    st.subheader('1. Analysis about the trend of the coming guests')
    # create a date select
    # st.write('**Please select a date to see the number of guests arriving at the hotels at that day**')
    date = st.date_input(
        'The exact date of arrival',
        datetime.date(2015,7,27),
        min_value=datetime.date(2015,7,1),
        max_value=datetime.date(2017,8,31)
        )
    date = str(date)
    st.write('**The chosen arrival date is**', date)
    day_guests = NumberOfGuests_Daily['Total Guests'][date]
    st.write('**The number of the guests of the day you chosen is** ', day_guests)
    st.write('The form of the daily number of gusets', NumberOfGuests_Daily)
    # show the plot
    st.subheader("Guests per day trend.")
    fig, ax = plt.subplots()  # Create a figure containing a single axes.
    x = NumberOfGuests_Daily['Total Guests'].keys()
    y = NumberOfGuests_Daily['Total Guests'].values
    ax.plot(x, y);  # Plot some data on the axes.
    st.pyplot(fig)

    # week day
    lis=[]
    for x in NumberOfGuests_Daily.index:
        lis.append(x.day_name())
    days = pd.DataFrame(lis,columns =['Day'])

    NumberOfGuestsDaily=NumberOfGuests_Daily.copy()
    NumberOfGuestsDaily.reset_index(drop=True, inplace=True)

    NumberOfGuestsDaily = NumberOfGuestsDaily.join(days)
    st.subheader("Guests per week day")
    st.bar_chart(x="Day", y="Total Guests", data=NumberOfGuestsDaily)

    # month
    lis=[]
    for x in NumberOfGuests_Daily.index:
        lis.append(x.month_name())
    days = pd.DataFrame(lis,columns =['Day'])

    NumberOfGuestsMonthly=NumberOfGuests_Daily.copy()
    NumberOfGuestsMonthly.reset_index(drop=True, inplace=True)

    NumberOfGuestsMonthly = NumberOfGuestsMonthly.join(days)
    NumberOfGuestsMonthly.rename(columns = {'Day':'Month'}, inplace = True)
    st.subheader("Guests per months")
    st.bar_chart(x="Month", y="Total Guests", data=NumberOfGuestsMonthly)

    months = [
        "January", "February", "March", "April", 
        "May", "June", "July", "August", "September",
        "October", "November", "December"]

    datastill.groupby(['arrival_date_month'])['hotel'].count().sort_values(ascending=False)
    sns.countplot(x='arrival_date_month', data=datastill, order=months)
    plt.xticks(rotation=90)
    plt.rcParams['figure.figsize'] = (13, 6)
    plt.show()
    st.pyplot(plt)
elif level_fliter =='Daily rate':
    #   ----------------------part2------------------------------------------
    st.subheader('2. Analysis about the daily rate of the hotels')
    
    df2 = datastill.drop(datastill[datastill['adr']==5400].index, axis=0, inplace=False)  # Removed an extreme outlier (adr=5400) that made boxplot very squeezed to view
    
    col1, col2 = st.columns([1,3])

    with col1:
        fig_fliter = st.radio(
            'Choose different figures',
            ('box','hist','line')
            )
    with col2:
        if fig_fliter == 'box':
            plt.figure(figsize=(10,10))
            sns.boxplot(x='hotel', y='adr', data = df2)
            plt.ylabel('Average daily rate')
            plt.xlabel("Hotel Type")
            plt.title("Daily Rate by hotel type")
            st.pyplot(plt)
        elif fig_fliter == 'hist':
            plt.figure(figsize=(9,6))
            sns.histplot(x='adr', hue='hotel', data=df2, kde=True)
            plt.xlabel("Average daily rate")
            plt.title("Daily rate by hotel type")
            st.pyplot(plt)
            st.write('We can see that the avg daily rate for Resort Hotels are more spread compared to City Hotels although have lesser median rate.')
        else:
            d = data.groupby(['hotel','arrival_date'])['adr'].mean().reset_index().sort_values('arrival_date')
            # fig = plt.figure(figsize=(20,7))
            fig, ax = plt.subplots(figsize=(20, 7))
            sns.lineplot(x='arrival_date', y='adr', hue='hotel', data=d)
            plt.xlabel("Date")
            plt.ylabel("Average Daily Price")
            plt.grid()
            #  fig.autofmt_xdate()
            p = plt.xticks(rotation=30)
            ax.tick_params(axis='x', labelsize=3)
            plt.title("Average daily rate trend over three years")
            st.pyplot(plt)
else:
    # ---------------------- part 3------------------------------------
    st.subheader('3. Customer group persona')

    data = datastill['customer_type'].value_counts()   
    print(data)
    labels = datastill['customer_type'].unique()
     
    col1, col2 = st.columns([1,2])

    with col1:
        st.markdown(
            '''
            **Customer type**  

            **Contract:** when the booking has an allotment or other type of contract associated to it  

            **Group:** when the booking is associated to a group  

            **Transient:** when the booking is not part of a group or contract, and is not associated to other transient booking  

            **Transient-party:** when the booking is transient, but is associated to at least other transient booking
            ''')
            
    with col2:
        explode = (0.1, 0.1, 0.2, 0.4)
        plt.figure(figsize =(10, 8))
        plt.pie(data,labels=labels, explode=explode, autopct='%.2f')
        st.pyplot(plt)
    

    d = datastill['country'].value_counts()
    plt.figure(figsize=(10,6))
    d.sort_values(ascending=False)[:10].plot(kind='bar')
    p = plt.xticks(rotation=30)
    plt.xlabel("Country")
    plt.ylabel("Number of bookings")
    plt.title("Top 10 countries by number of guests")
    st.pyplot(plt)
    st.write()
    st.write('The country of Portugal (PRT) has significantly higher number of bookings compared to any other countries.')
    
    d = datastill.groupby("customer_type")['total_of_special_requests'].mean()
    plt.figure(figsize=(8,7))
    sns.barplot(x=d.index, y=d)
    p = plt.xticks(rotation=30)
    plt.xlabel("Customer Type")
    plt.ylabel("Avg number of special request")
    plt.title("Average number of special requests by customer type")
    st.pyplot(plt)
    st.subheader('Customer preference')
    type_fliter = st.radio(
        'choose condition',
        ('By country','By customer type')
    )
    if type_fliter == 'By country':
        d = datastill['country'].value_counts().sort_values(ascending=False)[:10]
        plt.figure(figsize=(10,5))
        sns.countplot(x='country', hue='hotel', data=datastill[datastill['country'].isin(d.index)])
        plt.xlabel("Country")
        plt.ylabel("No. of Bookings")
        plt.title("Booked Hotel type by country")
        st.pyplot(plt)
    else:
        plt.figure(figsize=(8,5))
        sns.countplot(x='customer_type', hue='hotel', data=datastill)
        plt.xlabel("Customer Type")
        plt.ylabel("Number of Bookings made")
        plt.title("Hotel Preference by customer type")
        st.pyplot(plt)