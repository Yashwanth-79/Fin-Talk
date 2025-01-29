import os
from neo4j import GraphDatabase
from typing import List, Dict
from data import data
import json

# --------------------------- Neo4j Connection Details --------------------------- #
NEO4J_URI = "neo4j+s://59b6d873.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "XHs0ISCcQrrGYkg580ENlVIjdxFZOZkq6W0VcP7IkBk"

# --------------------------- GRAPH POPULATION FUNCTION --------------------------- #
def create_nodes_and_relationships(news_data: List[Dict]):
    """
    Convert the result string into nodes and relationships to be added to Neo4j.
    :param news_data: List of dictionaries containing the cleaned and processed news data.
    """
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        for article in news_data:
            try:
                title = article["Title"]
                entities = article["Entities"].split("; ") if article.get("Entities") else []
                sentiment = article.get("Sentiment", "")
                relationship = article.get("Relationship", "")
                source = article.get("Source", "")

                # Create article node
                session.run(
                    "MERGE (a:Article {title: $title, source: $source})",
                    title=title,
                    source=source
                )

                # Create nodes for each entity and create relationships to the article
                for entity in entities:
                    if " (" in entity:
                        entity_name, entity_type = entity.rsplit(" (", 1)
                        entity_type = entity_type.rstrip(")")
                        session.run(
                            """
                            MERGE (e:Entity {name: $name, type: $type})
                            MERGE (a:Article {title: $title})-[:MENTIONS]->(e)
                            """,
                            name=entity_name.strip(),
                            type=entity_type.strip(),
                            title=title
                        )

                # Create sentiment node and relationship
                if sentiment:
                    session.run(
                        """
                        MERGE (s:Sentiment {sentiment: $sentiment})
                        MERGE (a:Article {title: $title})-[:HAS_SENTIMENT]->(s)
                        """,
                        sentiment=sentiment,
                        title=title
                    )

                # Create relationship node (if any)
                if relationship:
                    session.run(
                        """
                        MERGE (r:Relationship {description: $relationship})
                        MERGE (a:Article {title: $title})-[:DESCRIBES]->(r)
                        """,
                        relationship=relationship,
                        title=title
                    )

            except Exception as e:
                print(f"Error creating nodes or relationships for article '{title}': {e}")

    driver.close()


# --------------------------- GRAPH VISUALIZATION --------------------------- #
def generate_html_visualization(cypher_query: str, output_file: str = "graph.html"):
    """
    Generates an HTML file with the graph visualization using vis.js.
    :param cypher_query: Cypher query to fetch graph data.
    :param output_file: Name of the output HTML file.
    """
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        try:
            # Fetch graph data from Neo4j
            result = session.run(cypher_query)
            nodes = {}
            edges = []

            for record in result:
                for node in record["p"].nodes:
                    node_id = node.id
                    label = node.get("title", node.get("name", str(node.id)))
                    if node_id not in nodes:
                        nodes[node_id] = {"id": node_id, "label": label}

                for relationship in record["p"].relationships:
                    edges.append({
                        "from": relationship.start_node.id,
                        "to": relationship.end_node.id,
                        "label": relationship.type
                    })

            nodes_list = list(nodes.values())

            # Generate HTML with vis.js
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Graph Visualization</title>
                <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js"></script>
                <style>
                    #network {{
                        width: 100%;
                        height: 600px;
                        border: 1px solid lightgray;
                    }}
                </style>
            </head>
            <body>
                <div id="network"></div>
                <script>
                    var nodes = new vis.DataSet({json.dumps(nodes_list)});
                    var edges = new vis.DataSet({json.dumps(edges)});

                    var container = document.getElementById("network");
                    var data = {{ nodes: nodes, edges: edges }};
                    var options = {{
                        nodes: {{
                            shape: "dot",
                            size: 20,
                            font: {{ size: 14 }}
                        }},
                        edges: {{
                            arrows: "to",
                            smooth: true
                        }},
                        physics: {{
                            stabilization: false
                        }}
                    }};

                    var network = new vis.Network(container, data, options);
                </script>
            </body>
            </html>
            """

            # Write the HTML content to a file
            with open(output_file, "w") as file:
                file.write(html_content)

            print(f"Graph visualization saved to {output_file}. Open it in a browser to view.")

        except Exception as e:
            print(f"Error generating HTML visualization: {e}")

    driver.close()


# --------------------------- MAIN FUNCTION --------------------------- #
def process_and_visualize_data(news_data):
    """
    Process the raw data, populate Neo4j, and visualize the graph.
    :param news_data: Raw cleaned data from the news API.
    """
    # Step 1: Convert the data to Neo4j compatible format (nodes & relationships)
    create_nodes_and_relationships(news_data)

    # Step 2: Visualize the graph by running Cypher queries
    cypher_query_sentiment = "MATCH p=()-[r:HAS_SENTIMENT]->() RETURN p LIMIT 25;"
    cypher_query_relationship = "MATCH p=()-[r:DESCRIBES]->() RETURN p LIMIT 25;"

    print("Generating HAS_SENTIMENT graph visualization...")
    generate_html_visualization(cypher_query_sentiment, "sentiment_graph.html")

    print("Generating DESCRIBES graph visualization...")
    generate_html_visualization(cypher_query_relationship, "relationship_graph.html")


# --------------------------- Run the process to populate Neo4j and visualize the graph --------------------------- #
process_and_visualize_data(data)
