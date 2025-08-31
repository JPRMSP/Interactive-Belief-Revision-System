import streamlit as st
from sympy.logic.boolalg import to_cnf, And
from sympy.parsing.sympy_parser import parse_expr
from sympy import satisfiable
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

st.set_page_config(page_title="Belief Revision Demo", page_icon="🧠", layout="wide")

st.title("🧠 Interactive Belief Revision System")
st.write("A real-time demo of **Belief Revision (AGM Theory)** with logical reasoning and visualization.")

# Belief base stored as session state
if "beliefs" not in st.session_state:
    st.session_state.beliefs = []

def is_consistent(beliefs):
    """Check consistency using sympy satisfiability."""
    if not beliefs:
        return True
    formula = And(*beliefs)
    return bool(satisfiable(formula))

def revise_beliefs(new_belief):
    """AGM-style revision: keep consistency by dropping least entrenched belief if needed."""
    st.session_state.beliefs.append(new_belief)
    while not is_consistent(st.session_state.beliefs):
        # remove the first (least entrenched) belief
        st.session_state.beliefs.pop(0)

# -------------------
# Belief Visualization
# -------------------
def visualize_beliefs(beliefs):
    G = nx.DiGraph()
    for i, belief in enumerate(beliefs):
        G.add_node(str(belief), label=f"Belief {i+1}")
        # Naive parse: link atoms inside a belief
        for atom in str(belief).replace("(", "").replace(")", "").replace("~", "").replace(" ", ""):
            if atom.isalpha():
                G.add_node(atom, label=atom)
                G.add_edge(atom, str(belief))

    net = Network(height="400px", width="100%", bgcolor="#222", font_color="white", directed=True)
    net.from_nx(G)
    net.repulsion(node_distance=150, spring_length=200)

    net.save_graph("belief_graph.html")
    with open("belief_graph.html", "r", encoding="utf-8") as f:
        components.html(f.read(), height=450, scrolling=True)

# -------------------
# UI Elements
# -------------------
st.subheader("📌 Current Belief Base")
st.write([str(b) for b in st.session_state.beliefs] if st.session_state.beliefs else "No beliefs yet.")

# Add new belief
new_belief_input = st.text_input("Enter new belief (e.g., A, ~A, A>>B):")
if st.button("Revise with new belief") and new_belief_input:
    try:
        parsed = to_cnf(parse_expr(new_belief_input.replace("~", "Not")))
        revise_beliefs(parsed)
        st.success(f"Belief '{new_belief_input}' added with revision.")
    except Exception as e:
        st.error(f"Invalid input: {e}")

# Remove belief
remove_choice = st.selectbox("Remove a belief (contraction):", ["None"] + [str(b) for b in st.session_state.beliefs])
if st.button("Contract Belief") and remove_choice != "None":
    st.session_state.beliefs = [b for b in st.session_state.beliefs if str(b) != remove_choice]
    st.info(f"Belief '{remove_choice}' removed (contraction applied).")

st.subheader("🔍 Consistency Check")
if is_consistent(st.session_state.beliefs):
    st.success("✅ Belief base is consistent.")
else:
    st.error("❌ Belief base is inconsistent!")

st.subheader("🌐 Belief Graph Visualization")
if st.session_state.beliefs:
    visualize_beliefs(st.session_state.beliefs)
else:
    st.write("No beliefs to visualize yet.")
