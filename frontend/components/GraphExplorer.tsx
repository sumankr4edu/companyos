"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import dynamic from "next/dynamic";

const ForceGraph2D = dynamic(
  () => import("react-force-graph-2d"),
  {
    ssr: false,
  },
);

type GraphNode = {
  id: string;
  name?: string;
  type?: string;
  label?: string;
  properties?: Record<string, unknown>;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number | null;
  fy?: number | null;
};

type GraphLink = {
  id?: string;
  source: string | GraphNode;
  target: string | GraphNode;
  type?: string;
  label?: string;
  properties?: Record<string, unknown>;
};

type ForceGraphData = {
  nodes: GraphNode[];
  links: GraphLink[];
};

type GraphExplorerProps = {
  nodes?: unknown[];
  relationships?: unknown[];
};

function normalizeNode(node: unknown, index: number): GraphNode {
  if (!node || typeof node !== "object") {
    return {
      id: `node-${index}`,
      name: `Node ${index + 1}`,
      type: "Unknown",
    };
  }

  const value = node as Record<string, unknown>;

  const id =
    value.id ??
    value.element_id ??
    value.identity ??
    `node-${index}`;

  const name =
    value.name ??
    value.title ??
    value.label ??
    id;

  const type =
    value.type ??
    value.entity_type ??
    value.label ??
    "Entity";

  return {
    id: String(id),
    name: String(name),
    type: String(type),
    label: String(name),
    properties:
      typeof value.properties === "object" &&
      value.properties !== null
        ? (value.properties as Record<string, unknown>)
        : value,
  };
}

function getEndpointId(endpoint: unknown): string | null {
  if (typeof endpoint === "string") {
    return endpoint;
  }

  if (typeof endpoint === "number") {
    return String(endpoint);
  }

  if (!endpoint || typeof endpoint !== "object") {
    return null;
  }

  const value = endpoint as Record<string, unknown>;

  const id =
    value.id ??
    value.element_id ??
    value.identity ??
    value.name;

  return id !== undefined && id !== null
    ? String(id)
    : null;
}

function normalizeRelationship(
  relationship: unknown,
  index: number,
  nodes: GraphNode[],
): GraphLink | null {
  if (!relationship || typeof relationship !== "object") {
    return null;
  }

  const value = relationship as Record<string, unknown>;

  const source =
    value.source ??
    value.start ??
    value.from ??
    value.source_id ??
    value.start_id;

  const target =
    value.target ??
    value.end ??
    value.to ??
    value.target_id ??
    value.end_id;

  let sourceId = getEndpointId(source);
  let targetId = getEndpointId(target);

  /*
   * Some FalkorDB relationship serializers return:
   *
   * {
   *   source: { id: "..." },
   *   target: { id: "..." }
   * }
   *
   * Others may return:
   *
   * {
   *   start: "...",
   *   end: "..."
   * }
   *
   * Normalize both forms.
   */

  if (!sourceId || !targetId) {
    return null;
  }

  /*
   * Make sure the relationship points to nodes that actually
   * exist in the graph.
   */
  const nodeIds = new Set(nodes.map((node) => node.id));

  if (!nodeIds.has(sourceId) || !nodeIds.has(targetId)) {
    return null;
  }

  const relationshipType =
    value.type ??
    value.label ??
    value.relation_type ??
    value.relationship_type ??
    "RELATED_TO";

  return {
    id:
      value.id !== undefined
        ? String(value.id)
        : `link-${index}`,
    source: sourceId,
    target: targetId,
    type: String(relationshipType),
    label: String(relationshipType),
    properties:
      typeof value.properties === "object" &&
      value.properties !== null
        ? (value.properties as Record<string, unknown>)
        : value,
  };
}

export default function GraphExplorer({
  nodes = [],
  relationships = [],
}: GraphExplorerProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  const [width, setWidth] = useState(900);
  const [height, setHeight] = useState(560);
  const [selectedNode, setSelectedNode] =
    useState<GraphNode | null>(null);

  useEffect(() => {
    if (!containerRef.current) {
      return;
    }

    const element = containerRef.current;

    const updateSize = () => {
      const rect = element.getBoundingClientRect();

      if (rect.width > 0) {
        setWidth(Math.floor(rect.width));
      }

      if (rect.height > 0) {
        setHeight(Math.floor(rect.height));
      }
    };

    updateSize();

    const observer = new ResizeObserver(updateSize);

    observer.observe(element);

    return () => {
      observer.disconnect();
    };
  }, []);

  const normalizedNodes = useMemo<GraphNode[]>(() => {
    return nodes.map((node, index) =>
      normalizeNode(node, index),
    );
  }, [nodes]);

  const normalizedLinks = useMemo<GraphLink[]>(() => {
    return relationships
      .map((relationship, index) =>
        normalizeRelationship(
          relationship,
          index,
          normalizedNodes,
        ),
      )
      .filter(
        (link): link is GraphLink =>
          link !== null,
      );
  }, [relationships, normalizedNodes]);

  const graphData = useMemo<ForceGraphData>(
    () => ({
      nodes: normalizedNodes,
      links: normalizedLinks,
    }),
    [normalizedNodes, normalizedLinks],
  );

  const getNodeLabel = (node: GraphNode): string => {
    return node.name || node.label || node.id;
  };

  const getNodeType = (node: GraphNode): string => {
    return node.type || "Entity";
  };

  const getNodeRadius = (node: GraphNode): number => {
    if (selectedNode?.id === node.id) {
      return 9;
    }

    return 6;
  };

  const handleNodeClick = (node: GraphNode) => {
    setSelectedNode(node);
  };

  const handleBackgroundClick = () => {
    setSelectedNode(null);
  };

  return (
    <div className="graph-explorer">
      <div className="graph-toolbar">
        <div className="graph-toolbar-stat">
          <span>Nodes</span>
          <strong>{normalizedNodes.length}</strong>
        </div>

        <div className="graph-toolbar-stat">
          <span>Relationships</span>
          <strong>{normalizedLinks.length}</strong>
        </div>

        {selectedNode && (
          <button
            type="button"
            className="graph-clear-button"
            onClick={() => setSelectedNode(null)}
          >
            Clear selection
          </button>
        )}
      </div>

      <div
        ref={containerRef}
        className="graph-canvas"
      >
        {normalizedNodes.length === 0 ? (
          <div className="graph-empty">
            <div className="graph-empty-icon">◎</div>
            <h4>No graph entities</h4>
            <p>
              FalkorDB did not return graph nodes for
              this investigation.
            </p>
          </div>
        ) : (
          <ForceGraph2D
            width={width}
            height={height}
            graphData={graphData}
            backgroundColor="rgba(0,0,0,0)"
            nodeLabel={(node: GraphNode) =>
              `${getNodeLabel(node)} · ${getNodeType(node)}`
            }
            nodeRelSize={6}
            nodeVal={(node: GraphNode) =>
              getNodeRadius(node)
            }
            nodeCanvasObject={(
              node: GraphNode,
              ctx: CanvasRenderingContext2D,
              globalScale: number,
            ) => {
              const x = Number(node.x ?? 0);
              const y = Number(node.y ?? 0);

              const radius = getNodeRadius(node);

              ctx.beginPath();
              ctx.arc(
                x,
                y,
                radius,
                0,
                2 * Math.PI,
              );

              ctx.fillStyle =
                selectedNode?.id === node.id
                  ? "#2d8cff"
                  : "#00d9ff";

              ctx.shadowBlur = 14;
              ctx.shadowColor =
                selectedNode?.id === node.id
                  ? "#2d8cff"
                  : "#00d9ff";

              ctx.fill();

              ctx.shadowBlur = 0;

              const label = getNodeLabel(node);

              const fontSize = Math.max(
                9,
                12 / Math.max(globalScale, 0.5),
              );

              ctx.font = `${fontSize}px Inter, Arial, sans-serif`;

              ctx.textAlign = "center";
              ctx.textBaseline = "top";

              ctx.fillStyle = "#e8f2ff";

              ctx.fillText(
                label,
                x,
                y + radius + 4,
              );
            }}
            linkColor={() => "rgba(45, 140, 255, 0.35)"}
            linkWidth={1.5}
            linkDirectionalArrowLength={4}
            linkDirectionalArrowRelPos={1}
            linkDirectionalParticles={1}
            linkDirectionalParticleWidth={2}
            linkDirectionalParticleSpeed={0.006}
            onNodeClick={handleNodeClick}
            onBackgroundClick={handleBackgroundClick}
            cooldownTicks={100}
            d3AlphaDecay={0.025}
            d3VelocityDecay={0.25}
          />
        )}

        {selectedNode && (
          <aside className="graph-inspector">
            <div className="graph-inspector-header">
              <div>
                <span>ENTITY</span>
                <h4>
                  {getNodeLabel(selectedNode)}
                </h4>
              </div>

              <button
                type="button"
                onClick={() =>
                  setSelectedNode(null)
                }
                aria-label="Close inspector"
              >
                ×
              </button>
            </div>

            <div className="graph-inspector-type">
              {getNodeType(selectedNode)}
            </div>

            <div className="graph-inspector-id">
              <span>ID</span>
              <code>{selectedNode.id}</code>
            </div>

            <div className="graph-properties">
              {Object.entries(
                selectedNode.properties ?? {},
              )
                .slice(0, 12)
                .map(([key, value]) => (
                  <div
                    className="graph-property"
                    key={key}
                  >
                    <span>{key}</span>
                    <strong>
                      {typeof value === "object"
                        ? JSON.stringify(value)
                        : String(value)}
                    </strong>
                  </div>
                ))}
            </div>
          </aside>
        )}
      </div>
    </div>
  );
}