import streamlit as st
import numpy as np
import pandas as pd
import random
import gurobipy as gp
from gurobipy import GRB,quicksum


st.title('Student University Matching')

st.image("https://mlhxjisu2gky.i.optimole.com/hv2pyxI-VDXJoKT8/w:1160/h:390/q:82/https://www.clearadmit.com/wp-content/uploads/2017/09/4422_London-Business-School-Sammy-Ofer-Centre_07.jpg")

st.subheader("We try to optimize student's happiness")

st.sidebar.write("Select number of available seats")
lbs_seats = st.sidebar.slider("LBS", min_value=1, max_value=1000, step=10, value=100)
lse_Seats = st.sidebar.slider("LSE", min_value=1, max_value=1000, step=10, value=100)
warwick_seats = st.sidebar.slider("Warwick", min_value=1, max_value=1000, step=10, value=100)
imperial_seats = st.sidebar.slider("Imperial", min_value=1, max_value=1000, step=10, value=100)
oxford_seats = st.sidebar.slider("Oxford", min_value=1, max_value=1000, step=10, value=100)

uni_av = {
    0:lbs_seats,
    1:lse_Seats,
    2:warwick_seats,
    3:imperial_seats,
    4:oxford_seats
}

uni_prob = {
    0:0.4,
    1:0.2,
    2:0.1,
    3:0.05
}

uni_min_gpa = {
    0:3.5,
    1:3,
    2:2.5,
    3:0,
    4:0
}

student_num = st.slider("Number of Students", min_value=100, max_value=10000, step=100, value=500)

students_gpa = []
for i in range(0,student_num):
    students_gpa.append(random.randint(20,40)/10)


def get_ranking():
    unis = [0,1,2,3,4]
    result = []
    while unis:
        r = random.random()
        if r > uni_prob[0] and 0 in unis:
            result.append(0)
            unis.remove(0)
            continue
        elif r > uni_prob[1] and 1 in unis:
            result.append(1)
            unis.remove(1)
            continue
        elif r > uni_prob[2] and 2 in unis:
            result.append(2)
            unis.remove(2)
            continue
        elif r > uni_prob[3] and 3 in unis:
            result.append(3)
            unis.remove(3)
            continue
        elif 4 in unis:
            result.append(4)
            unis.remove(4)
    return result


students_choices = []
for i in range(0,student_num):
    students_choices.append(get_ranking())

df = pd.DataFrame(students_choices, columns = [0, 1, 2, 3, 4])
df = df.to_numpy()

pref=np.zeros((student_num,5), dtype=int)

for i in range (0,student_num, 1):
    for j in range (0, 5, 1):
        k=df[i][j]
        pref[i, k]=5-j


df_pref = pd.DataFrame(pref)

# Model

m = gp.Model("students")

students = np.arange(0,student_num,1).tolist()
unis = np.arange(0, 5, 1).tolist()

allocation_uni= m.addVars(students,unis, name="uni_binary", vtype=GRB.BINARY)

for u in unis:
    m.addConstr(quicksum(allocation_uni[s,u] for s in students) <= uni_av[u])

for s in students:
    m.addConstr(quicksum(allocation_uni[s,u] for u in unis) <= 1)

#creating the auxilliary variable
auxilliary = m.addVars(students, unis, vtype = GRB.BINARY, name = "auxillary variable")

M = 10000000

for u in unis:
    for s in students:
        m.addConstr(students_gpa[s] >= uni_min_gpa[u] - M*(1-auxilliary[s,u]))
        m.addConstr(allocation_uni[s,u] <= M*auxilliary[s,u])



m.setObjective(quicksum(allocation_uni[s,u]*df_pref[u][s] for s in students for  u in unis), GRB.MAXIMIZE)

m.optimize()


choice_1, choice_2, choice_3, choice_4, choice_5 = 0,0,0,0,0

for s in students:
    for u in unis:
        value=df_pref[u][s]*allocation_uni[s,u]
        if value.getValue()==5:
            choice_1+=1
            continue
        if value.getValue()==4:
            choice_2+=1
            continue
        if value.getValue()==3:
            choice_3+=1
            continue
        if value.getValue()==2:
            choice_4+=1
            continue
        if value.getValue()==1:
            choice_5+=1


left_column, right_column = st.columns(2)

with left_column:
    st.subheader("Business Schools:")
    st.write("* LBS: Rank 1 for 60% of students but only accept students with GPAs above 3.5")
    st.write("* LSE: Rank 1 for 20% of students but only accept students with GPAs above 3")
    st.write("* Warwick: Rank 1 for 10% of students but only accept students with GPAs above 2.5")
    st.write("* Imperial: Rank 1 for 5% of students and accept all students")
    st.write("* Oxford: Rank 1 for 5% of students and accept all students")


with right_column:
    st.subheader("Students happiness:")
    st.write("* If a student is alocated to his first choice, the happiness value will be 5.")
    st.write("* If a student is alocated to his second choice, the happiness value will be 4.")
    st.write("* If a student is alocated to his third choice, the happiness value will be 3.")
    st.write("* If a student is alocated to his fourth choice, the happiness value will be 2.")
    st.write("* If a student is alocated to his last choice, the happiness value will be 1.")


st.subheader('Result, students with:')
st.write('First choice:', choice_1)
st.write('Second choice:', choice_2)
st.write('Third choice:', choice_3)
st.write('Fourth choice:', choice_4)
st.write('Last choice:', choice_5)






