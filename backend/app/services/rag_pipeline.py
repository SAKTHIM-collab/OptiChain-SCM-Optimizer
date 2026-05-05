import os
import pandas as pd
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DataFrameLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

# 1. Load Data
data_path = os.path.join(os.getcwd(), "data", "inventory_data.csv")
df = pd.read_csv(data_path)

# 2. Convert CSV rows into LangChain Documents
loader = DataFrameLoader(df, page_content_column="Product_Name")
documents = loader.load()

# 3. Create Vector Database (Chroma)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = Chroma.from_documents(documents, embeddings, persist_directory="./chroma_db")
retriever = vector_store.as_retriever(search_kwargs={"k": 3})


# 4. Setup the LLM (Groq)
llm = ChatGroq(
    temperature=0, 
    model_name="llama-3.1-8b-instant", 
    api_key=os.environ.get("GROQ_API_KEY")
)

# 5. Define the Professional Prompt
system_prompt = (
    "You are an elite Supply Chain Analyst AI for an FMCG company. "
    "Use the following pieces of retrieved inventory context to answer the user's question. "
    "If the context shows Current_Stock is below the Reorder_Point, explicitly warn about a potential stockout. "
    "Always consider Lead_Time_Days and Supplier_Constraints in your recommendations. "
    "If you don't know the answer based on the context, say that you lack the data. Do not guess.\n\n"
    "Context: {context}"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])

# 6. Helper function to format the retrieved documents
def format_docs(docs):
    formatted_data = []
    for doc in docs:
        # Combine the product name with its hidden statistical data
        stats = ", ".join([f"{key}: {value}" for key, value in doc.metadata.items()])
        formatted_data.append(f"Product: {doc.page_content} | {stats}")
    return "\n\n".join(formatted_data)

# 7. The Modern LCEL Chain (Bypasses the broken 'chains' module)
rag_chain = (
    {"context": retriever | format_docs, "input": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

def generate_supply_chain_insight(user_query: str) -> str:
    """Executes the LCEL chain and returns the AI's response."""
    # With LCEL, we can invoke the chain directly with the string
    return rag_chain.invoke(user_query)