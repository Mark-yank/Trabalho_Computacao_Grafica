cores =['black','red','green','blue','purple']
i=0

def plot_wireframe_poligonos(vertices, triangular_faces, i):
    """
    Plota um wireframe 3D
    """
    added_edges = set()  # Para evitar arestas duplicadas

    for tri in triangular_faces:
        for a, b in [(0, 1), (1, 2), (2, 0)]:
            v1, v2 = tri[a], tri[b]
            edge = tuple(sorted((v1, v2)))
            if edge in added_edges:
                continue
            added_edges.add(edge)

            x = [vertices[v1][0], vertices[v2][0]]
            y = [vertices[v1][1], vertices[v2][1]]
            z = [vertices[v1][2], vertices[v2][2]]
            fig.add_trace(go.Scatter3d(
                x=x, y=y, z=z,
                mode='lines',
                line=dict(color=cores[i], width=4),
            ))

# Adiciona a reta 3D
def plot_wireframe_reta(vertices_reta,i):
    x_vals = [P1[0], P2[0]]
    y_vals = [P1[1], P2[1]]
    z_vals = [P1[2], P2[2]]

    fig.add_trace(go.Scatter3d(
    x=x_vals, y=y_vals, z=z_vals,
    mode='lines+markers',
    line=dict(color=cores[i], width=6),
    marker=dict(size=4, color=cores[i]),
    ))
