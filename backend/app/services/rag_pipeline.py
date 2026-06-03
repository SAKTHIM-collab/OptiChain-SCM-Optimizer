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

# 1. Load Data (UPDATED: Points to your new file)
data_path = os.path.join(os.getcwd(), "data", "supply_chain_data.csv")
df = pd.read_csv(data_path)

# Data Cleaning Pro-Tip: Replace spaces in columns with underscores 
# This makes dictionary lookup and prompt instructions much safer!
df.columns = df.columns.str.replace(' ', '_')

# 2. Convert CSV rows into LangChain Documents 
# (UPDATED: Using "SKU-Level_Detail" as the primary searchable column for this dataset)
loader = DataFrameLoader(df, page_content_column="SKU_ID")
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

# 5. Define the Professional Prompt (UPDATED: Re-aligned with your new dataset parameters)
# 5. Define the Professional Prompt (FIXED with your exact image column names)
system_prompt = (
    "You are an elite enterprise Supply Chain Analyst AI specialized in inventory health analytics.\n"
    "Use the following retrieved database context to answer the user's question accurately.\n\n"
    
    "When evaluating inventory efficiency, you must strictly follow this operations logic:\n"
    "1. Review the current 'Inventory_Level' against the baseline 'Reorder_Point' threshold.\n"
    "2. If 'Stockout_Flag' is equal to 1, immediately trigger an aggressive stockout warning.\n"
    "3. Factor in 'Supplier_Lead_Time', 'Order_Quantity', and 'Demand_Forecast' alongside regional parameters "
    "('Warehouse' and 'Region') to provide actionable logistics optimization recommendations.\n\n"
    
    "Ground all summaries strictly in the provided data text. If the context lacks information "
    "for the requested SKU_ID, say: 'I lack sufficient data for this item.' Do not hallucinate.\n\n"
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
        # Combines the primary SKU data with all its new metadata metrics
        stats = ", ".join([f"{key}: {value}" for key, value in doc.metadata.items()])
        formatted_data.append(f"SKU Detail: {doc.page_content} | {stats}")
    return "\n\n".join(formatted_data)

# 7. The Modern LCEL Chain
rag_chain = (
    {"context": retriever | format_docs, "input": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

def generate_supply_chain_insight(user_query: str) -> str:
    """Executes the LCEL chain and returns the AI's response."""
    return rag_chain.invoke(user_query)