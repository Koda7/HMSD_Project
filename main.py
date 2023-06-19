import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from numpy import ones, vstack
from numpy.linalg import lstsq
import numpy as np

if "uploaded" not in st.session_state:
    st.session_state.uploaded = False
    st.session_state.eflow_class = "A"

st.title("HMSD Project")

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """

st.markdown(hide_menu_style, unsafe_allow_html=True)


def calcEflow():
    st.session_state.uploaded = True
    st.session_state.eflow_class = st.session_state.e_class


def calcRelease(row):
    return row[1] + row[3] - row[2] - row[4]


uploaded_file = st.file_uploader(
    "Upload Resorvoir Information file (csv)", type=[".csv"]
)

with st.form("Environmental flow", clear_on_submit=False):
    eflow_class = st.selectbox(
        "Select Environmental Flow Class",
        [chr(ord("A") + i) for i in range(6)],
        key="e_class",
    )
    submit = st.form_submit_button("Submit", on_click=calcEflow)


def get_val_from_line(x1, y1, x2, y2, x):
    points = [(x1, y1), (x2, y2)]
    x_coords, y_coords = zip(*points)
    A = vstack([x_coords, ones(len(x_coords))]).T
    m, c = lstsq(A, y_coords, rcond=None)[0]
    return m * x + c


if uploaded_file is not None and st.session_state.uploaded:
    df = pd.read_csv(uploaded_file)
    df["Releases"] = df.apply(lambda row: calcRelease(row), axis=1)
    st.table(df)
    org_release = list(df["Releases"])
    release = org_release.copy()
    release.sort(reverse=True)
    temp_prob = []
    for val in org_release:
        temp_prob.append((release.index(val) + 1) / (len(org_release) + 1) * 100)
    len_release = len(release)
    mbynplusone = []
    for i in range(len(release)):
        mbynplusone.append((i + 1) / (len_release + 1))
    prob = []
    for x in mbynplusone:
        prob.append(x * 100)
    points = [(prob[0], release[0]), (prob[1], release[1])]
    x_coords, y_coords = zip(*points)
    A = vstack([x_coords, ones(len(x_coords))]).T
    m, c = lstsq(A, y_coords, rcond=None)[0]
    fig, ax = plt.subplots()
    ax.set_title("Flow Duration Curve")
    ax.set_xlabel("% Time Flow Exceedance")
    ax.set_ylabel("Flow")
    ax.plot(prob, release)
    st.pyplot(fig)
    val_to_find = [
        0.01,
        0.1,
        1,
        5,
        10,
        20,
        30,
        40,
        50,
        60,
        70,
        80,
        90,
        95,
        99,
        99.9,
        99.99,
    ]

    found_vals = []
    for val in val_to_find:
        if val < prob[0]:
            found_vals.append(
                get_val_from_line(prob[0], release[0], prob[1], release[1], val)
            )
        elif val > prob[-1]:
            found_vals.append(
                get_val_from_line(prob[-1], release[-1], prob[-2], release[-2], val)
            )
        else:
            if prob[-1] == val:
                found_vals.append(release[-1])
                continue
            for i in range(len(prob) - 1):
                if prob[i] == val:
                    found_vals.append(release[i])
                    break
                if prob[i] < val and prob[i + 1] > val:
                    found_vals.append(
                        get_val_from_line(
                            prob[i], release[i], prob[i + 1], release[i + 1], val
                        )
                    )
                    break
    fig, ax = plt.subplots()
    ax.set_xlabel("% Time Flow Exceedence")
    ax.set_ylabel("Flow")
    ax.plot(val_to_find, found_vals, label="Natural_flow")
    e_flow_class = {}
    for i in range(6):
        eclass = chr(ord("a") + i)
        e_flow_class[eclass] = [0 for _ in range(len(val_to_find))]
        ind = i + 1
        while ind < len(val_to_find):
            e_flow_class[eclass][ind - i - 1] = found_vals[ind]
            ind += 1
        ax.plot(val_to_find, e_flow_class[eclass], label="Class " + eclass.upper())
    ax.legend()
    ax.set_title("Environmental Flow FDC")
    st.pyplot(fig)
    chosen_class = st.session_state.eflow_class.lower()
    class_eflow = e_flow_class[chosen_class]
    envi_flow = []
    for val in temp_prob:
        if val < val_to_find[0]:
            envi_flow.append(
                get_val_from_line(
                    val_to_find[0], class_eflow[0], val_to_find[1], class_eflow[1], val
                )
            )
        elif val > val_to_find[-1]:
            envi_flow.append(
                get_val_from_line(
                    val_to_find[-1],
                    class_eflow[-1],
                    val_to_find[-2],
                    class_eflow[-2],
                    val,
                )
            )
        else:
            if val_to_find[-1] == val:
                envi_flow.append(class_eflow[-1])
                continue
            for i in range(len(val_to_find) - 1):
                if val_to_find[i] == val:
                    envi_flow.append(class_eflow[i])
                    break
                if val_to_find[i] < val and val_to_find[i + 1] > val:
                    envi_flow.append(
                        get_val_from_line(
                            val_to_find[i],
                            class_eflow[i],
                            val_to_find[i + 1],
                            class_eflow[i + 1],
                            val,
                        )
                    )
                    break
    fig, ax = plt.subplots()
    ax.plot([i for i in range(len(release))], org_release, label="Natural")
    ax.plot(
        [i for i in range(len(release))],
        envi_flow,
        label="Class %s" % (chosen_class.upper()),
    )
    ax.legend()
    ax.set_title("Time series Data")
    ax.set_xlabel("Month Number")
    ax.set_ylabel("Flow")
    st.pyplot(fig)
