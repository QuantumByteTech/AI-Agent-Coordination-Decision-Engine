\# AI Agent Coordination \& Decision Engine



An enterprise-oriented HR automation system developed as part of the Infosys Springboard Internship.



The project uses Google Gemini, multi-agent coordination, tool execution, Retrieval-Augmented Generation (RAG), and a vector database to answer employee HR queries using company-specific information.



\---



##### **## Project Overview**



The system is designed to act as an AI-powered HR assistant that can:



\- Answer company HR policy questions

\- Retrieve relevant HR policies using semantic search

\- Provide employee information through an external API

\- Route questions to specialized HR agents

\- Execute appropriate tools based on the employee's query

\- Generate clear natural-language responses using Google Gemini



The project was developed incrementally across internship milestones.



\---



##### **## Milestones**



\### Milestone 1 — Initial AI/LLM Prototype



The initial implementation explored a simple language-model based workflow using LangChain and Gemini.



The earlier implementation is retained separately as instructed by the project mentor.



\### Milestone 2 — Enterprise Workflow and Decision Automation



The system was extended into a multi-agent architecture with:



\- HR Assistant Agent

\- Policy Agent

\- Leave Agent

\- Coordinator Agent

\- Tool Selector

\- Tool Executor

\- Employee Information API

\- RAG-based HR policy retrieval

\- ChromaDB vector database

\- Gemini embeddings

\- Gemini language model



\---



##### **## System Architecture**





&#x20;                        Employee Query

&#x20;                              |

&#x20;                              v

&#x20;                    +--------------------+

&#x20;                    |  Coordinator Agent |

&#x20;                    +--------------------+

&#x20;                              |

&#x20;                              v

&#x20;                    +--------------------+

&#x20;                    |   Tool / Agent     |

&#x20;                    |     Selection      |

&#x20;                    +--------------------+

&#x20;                              |

&#x20;             +----------------+----------------+

&#x20;             |                |                |

&#x20;             v                v                v

&#x20;      Policy Agent       Leave Agent      HR Assistant

&#x20;             |                |                |

&#x20;             v                v                v

&#x20;       RAG / Policy       HR Policies     Employee API

&#x20;          Tool                                Tool

&#x20;             |                                  |

&#x20;             v                                  v

&#x20;         ChromaDB                         Employee Data

&#x20;      Vector Database

&#x20;             |

&#x20;             v

&#x20;     Relevant Information

&#x20;             |

&#x20;             v

&#x20;       Google Gemini

&#x20;             |

&#x20;             v

&#x20;      Natural-Language

&#x20;         HR Response



##### **RAG Workflow**



The HR policy information is stored in hr\_policies.txt.



The RAG pipeline works as follows:



hr\_policies.txt

&#x20;     |

&#x20;     v

Policy Sections

&#x20;     |

&#x20;     v

Gemini Embeddings

&#x20;     |

&#x20;     v

ChromaDB Vector Database

&#x20;     |

&#x20;     v

Employee Question

&#x20;     |

&#x20;     v

Query Embedding

&#x20;     |

&#x20;     v

Semantic Similarity Search

&#x20;     |

&#x20;     v

Relevant Policy Sections

&#x20;     |

&#x20;     v

Gemini

&#x20;     |

&#x20;     v

Final HR Response



This allows the system to retrieve policies based on meaning rather than relying only on exact keyword matches.



##### **Agents**

Coordinator Agent



The Coordinator determines which specialized agent should handle the employee's question.



Examples:



Work-from-home questions → Policy Agent

Leave questions → Leave Agent

Employee information → HR Assistant

Policy Agent



Handles company policy-related questions.



It uses the RAG pipeline to retrieve relevant information from the HR policy knowledge base.



Leave Agent



Handles employee leave-related queries using the company's leave policy.



HR Assistant



Acts as the general HR-facing agent and can handle employee information and other supported HR requests.



##### **Tools**

HR Policy Tool



Provides access to company HR policy information.



RAG Tool



Performs semantic retrieval using:



Gemini Embeddings

ChromaDB

Vector similarity search

Employee API Tool



Retrieves employee information using an external API.



Tool Selector



Determines which tool is appropriate for a given query.



Tool Executor



Executes the selected tool and returns a structured result.



Example Queries

Work From Home



Question:



What are the work from home rules?



Example response:



WFH may be requested when permitted by the employee's role and team.

Planned WFH requests require manager approval.

Employees must remain available during normal working hours.

Remote employees must have a stable internet connection.

Leave Policy



Question:



How many casual leaves do employees receive per year?



Example response:



Employees receive 12 casual leaves per calendar year.



Employee Information



Question:



What is the information for employee 1?



The system retrieves the employee information through the employee API and generates a readable HR response.



##### **Project Structure**



HR-Agent-Enterprise/

│

├── agents/

│   ├── coordinator.py

│   ├── hr\_agent.py

│   ├── leave\_agent.py

│   └── policy\_agent.py

│

├── tools/

│   ├── employee\_api\_tool.py

│   ├── hr\_policy\_tool.py

│   ├── rag\_tool.py

│   ├── tool\_executor.py

│   └── tool\_selector.py

│

├── hr\_policies.txt

│

├── agent\_action\_pipeline.py

│

├── test\_agent\_action\_pipeline.py

├── test\_coordinator.py

├── test\_gemini.py

├── test\_hr\_agent.py

├── test\_leave\_agent.py

├── test\_policy\_agent.py

└── test\_tool\_selector.py

│

├── requirements.txt

├── .gitignore

└── README.md



##### **Technologies Used**

Python

Google Gemini

Google GenAI SDK

Gemini Embeddings

ChromaDB

Retrieval-Augmented Generation (RAG)

LangChain (Milestone 1)

REST API

Python-dotenv



Installation

1\. Clone the repository

git clone <YOUR\_GITHUB\_REPOSITORY\_URL>

cd HR-Agent-Enterprise

2\. Create a virtual environment

python -m venv .venv

3\. Activate the environment



Windows PowerShell:



.venv\\Scripts\\Activate.ps1

4\. Install dependencies

pip install -r requirements.txt

Environment Variables



Create a .env file in the project root:



GEMINI\_API\_KEY=your\_gemini\_api\_key\_here



The .env file is intentionally excluded from GitHub using .gitignore.



Never upload your actual API key to a public repository.



Build the Vector Database



Before using the RAG system, create the ChromaDB vector database from the HR policy document:



python -c "from tools.rag\_tool import build\_vector\_database; print('Stored policy sections:', build\_vector\_database())"



The policy sections will be converted into embeddings and stored in the local ChromaDB database.



Test RAG Retrieval



Run:



python -c "from tools.rag\_tool import search\_hr\_policy\_rag; print(search\_hr\_policy\_rag('What are the work from home rules?'))"



The system should return the most relevant HR policy sections.



Run the Policy Agent

python test\_policy\_agent.py



Example:



Enter your HR policy question: What are the work from home rules?

Run the HR Assistant

python test\_hr\_agent.py



Example:



Enter your HR question: What is the information for employee 1?

Run the Coordinator

python test\_coordinator.py



The Coordinator routes the employee's query to the appropriate specialized agent.



##### **Tool Execution Pipeline**



The project also contains a structured action pipeline:



Employee Query

&#x20;     |

&#x20;     v

Validation

&#x20;     |

&#x20;     v

Tool Selection

&#x20;     |

&#x20;     v

Tool Execution

&#x20;     |

&#x20;     v

Tool Result



It supports validation and error handling for unsupported queries and invalid employee IDs.

##### 

##### **Error Handling**



The system handles cases such as:



Missing employee ID

Invalid employee ID format

Employee not found

Unknown tools

Missing policy information

Missing Gemini API key

Missing HR policy document



For unsupported HR questions, the system does not invent company-specific information and instead directs the employee to HR when appropriate.



##### **Future Scope**



Possible future improvements include:



Web-based HR dashboard

Authentication and employee access control

Real enterprise HR database integration

More HR policies and documents

Automated workflow approvals

HR ticket creation

Audit logs

More specialized HR agents

Production deployment

Enterprise-grade vector database



##### **Disclaimer**



This project is an internship/demo implementation. The employee API and HR policy data used in the project are demonstration data and are not intended to represent a real organization's confidential HR systems.

