import numpy as np
import plotly.graph_objects as go

def create_closed_box_triangles(base, comprimento, altura, origem=[0,0,0]):
    """
    Cria os vértices e faces triangulares de um paralelepípedo.
    """
    ox=origem[0]
    oy=origem[1]
    oz=origem[2]
    half_base = base / 2
    half_comprimento = comprimento / 2

    vertices = np.array([
        [ox-half_base, oy-half_comprimento, 0],         # V0
        [ox+half_base, oy-half_comprimento, 0],         # V1
        [ox+half_base, oy+half_comprimento, 0],         # V2
        [ox-half_base, oy+half_comprimento, 0],         # V3
        [ox-half_base, oy-half_comprimento, oz+altura],    # V4
        [ox+half_base, oy-half_comprimento, oz+altura],    # V5
        [ox+half_base, oy+half_comprimento, oz+altura],    # V6
        [ox-half_base, oy+half_comprimento, oz+altura],    # V7
    ])

    # Cada face quadrada dividida em dois triângulos
    triangular_faces = [
        [0, 1, 2], [0, 2, 3],  # base
        [4, 5, 6], [4, 6, 7],  # topo
        [0, 1, 5], [0, 5, 4],  # traseira
        [1, 2, 6], [1, 6, 5],  # direita
        [2, 3, 7], [2, 7, 6],  # frente
        [3, 0, 4], [3, 4, 7],  # esquerda
    ]

    return vertices, triangular_faces


def hermite(p0, t0, p1, t1, num_points=100):
    t = np.linspace(0, 1, num_points)
    h00 = 2 * t**3 - 3 * t**2 + 1
    h10 = t**3 - 2 * t**2 + t
    h01 = -2 * t**3 + 3 * t**2
    h11 = t**3 - t**2
    return (h00[:, None] * p0 + h10[:, None] * t0 +
            h01[:, None] * p1 + h11[:, None] * t1)

def generate_cano_com_espessura_hermite(p0, p1, t0, t1, outer_radius, thickness, num_points=40, num_circle_points=30):
    inner_radius = outer_radius - thickness
    curve_points = hermite(p0, t0, p1, t1, num_points)
    outer_rings = []
    inner_rings = []

    theta = np.linspace(0, 2 * np.pi, num_circle_points, endpoint=False)

    for i in range(len(curve_points) - 1):
        center = curve_points[i]
        next_center = curve_points[i + 1]

        direction = next_center - center
        direction = direction / np.linalg.norm(direction)

        # Geração da base ortonormal
        a = np.array([1, 0, 0])
        if np.allclose(direction, a):
            a = np.array([0, 1, 0])
        b = np.cross(direction, a)
        b = b / np.linalg.norm(b)
        a = np.cross(b, direction)

        # Gera círculo externo e interno
        def make_ring(radius):
            return [center + radius * (np.cos(angle) * a + np.sin(angle) * b) for angle in theta]

        outer_rings.append(np.array(make_ring(outer_radius)))
        inner_rings.append(np.array(make_ring(inner_radius)))

    return outer_rings, inner_rings

def triangulate_espessura_cano(outer_rings, inner_rings):
    """
    Gera triângulos para as paredes internas, externas e bocas do cano.
    """
    vertices = np.vstack(outer_rings + inner_rings)
    faces = []
    n = len(outer_rings)
    m = len(outer_rings[0])

    # Superfície externa
    for i in range(n - 1):
        for j in range(m):
            p0 = i * m + j
            p1 = i * m + (j + 1) % m
            p2 = (i + 1) * m + j
            p3 = (i + 1) * m + (j + 1) % m
            faces.append([p0, p1, p2])
            faces.append([p1, p3, p2])

    # Superfície interna
    offset = n * m
    for i in range(n - 1):
        for j in range(m):
            p0 = offset + i * m + j
            p1 = offset + i * m + (j + 1) % m
            p2 = offset + (i + 1) * m + j
            p3 = offset + (i + 1) * m + (j + 1) % m
            faces.append([p0, p2, p1])  # ordem invertida
            faces.append([p1, p2, p3])

    # Conexões nas bocas
    for j in range(m):
        # Boca inicial
        o0 = j
        o1 = (j + 1) % m
        i0 = offset + j
        i1 = offset + (j + 1) % m
        faces.append([o0, i1, i0])
        faces.append([o0, o1, i1])

        # Boca final
        o0 = (n - 1) * m + j
        o1 = (n - 1) * m + (j + 1) % m
        i0 = offset + (n - 1) * m + j
        i1 = offset + (n - 1) * m + (j + 1) % m
        faces.append([o0, i0, i1])
        faces.append([o0, i1, o1])

    return vertices, faces

def generate_cano_com_espessura(p0, p1, outer_radius, thickness, num_points=20, num_circle_points=30):
    """
    Gera dois conjuntos de anéis (externo e interno) ao longo do cano.
    """
    inner_radius = outer_radius - thickness
    t = np.linspace(0, 1, num_points)
    centers = (1 - t)[:, None] * p0 + t[:, None] * p1
    theta = np.linspace(0, 2 * np.pi, num_circle_points, endpoint=False)

    direction = p1 - p0
    direction = direction / np.linalg.norm(direction)
    a = np.array([1, 0, 0])
    if np.allclose(direction, a):
        a = np.array([0, 1, 0])
    b = np.cross(direction, a)
    b = b / np.linalg.norm(b)
    a = np.cross(b, direction)

    def generate_ring(center, radius):
        return [center + radius * (np.cos(angle) * a + np.sin(angle) * b) for angle in theta]

    outer_rings = [np.array(generate_ring(center, outer_radius)) for center in centers]
    inner_rings = [np.array(generate_ring(center, inner_radius)) for center in centers]

    return outer_rings, inner_rings

def triangulate_cano_com_espessura(outer_rings, inner_rings):
    """
    Gera os triângulos das paredes do cano com espessura.
    """
    vertices = np.vstack(outer_rings + inner_rings)
    faces = []
    n = len(outer_rings)
    m = len(outer_rings[0])  # num_circle_points

    # Lados externos
    for i in range(n - 1):
        for j in range(m):
            p0 = i * m + j
            p1 = i * m + (j + 1) % m
            p2 = (i + 1) * m + j
            p3 = (i + 1) * m + (j + 1) % m
            faces.append([p0, p1, p2])
            faces.append([p1, p3, p2])

    # Lados internos
    offset = n * m
    for i in range(n - 1):
        for j in range(m):
            p0 = offset + i * m + j
            p1 = offset + i * m + (j + 1) % m
            p2 = offset + (i + 1) * m + j
            p3 = offset + (i + 1) * m + (j + 1) % m
            # Inversão da ordem para manter normais corretas
            faces.append([p0, p2, p1])
            faces.append([p1, p2, p3])

    # Conexões entre anéis (boca da frente e de trás)
    for i in range(m):
        # Boca inicial
        o0 = i
        o1 = (i + 1) % m
        i0 = offset + i
        i1 = offset + (i + 1) % m
        faces.append([o0, i1, i0])
        faces.append([o0, o1, i1])

        # Boca final
        o0 = (n - 1) * m + i
        o1 = (n - 1) * m + (i + 1) % m
        i0 = offset + (n - 1) * m + i
        i1 = offset + (n - 1) * m + (i + 1) % m
        faces.append([o0, i0, i1])
        faces.append([o0, i1, o1])

    return vertices, faces

def generate_cilindro_fechado(p0, p1, radius, num_points=20, num_circle_points=30):
    t = np.linspace(0, 1, num_points)
    axis_points = (1 - t)[:, None] * p0 + t[:, None] * p1
    circle_points_list = []

    theta = np.linspace(0, 2 * np.pi, num_circle_points, endpoint=False)

    direction = p1 - p0
    direction = direction / np.linalg.norm(direction)

    # Base ortonormal do círculo
    a = np.array([1, 0, 0])
    if np.allclose(direction, a):
        a = np.array([0, 1, 0])
    b = np.cross(direction, a)
    b = b / np.linalg.norm(b)
    a = np.cross(b, direction)

    for center in axis_points:
        circle_points = []
        for angle in theta:
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            point = center + x * a + y * b
            circle_points.append(point)
        circle_points_list.append(np.array(circle_points))

    base_center = axis_points[0]
    top_center = axis_points[-1]
    base_circle = circle_points_list[0]
    top_circle = circle_points_list[-1]

    return {
        "axis_points": axis_points,
        "circle_points_list": circle_points_list,
        "base_center": base_center,
        "top_center": top_center,
        "base_circle": base_circle,
        "top_circle": top_circle
    }

def triangulate_cilindro_fechado(data):
    """
    Gera as faces triangulares do cilindro fechado (laterais + tampas).
    """
    circle_points_list = data["circle_points_list"]
    base_center = data["base_center"]
    top_center = data["top_center"]
    base_circle = data["base_circle"]
    top_circle = data["top_circle"]

    n_rings = len(circle_points_list)
    m = len(circle_points_list[0])  # pontos por círculo

    # Junta todos os vértices em um único array
    vertices = np.vstack(circle_points_list + [base_center, top_center])
    base_center_index = len(vertices) - 2
    top_center_index = len(vertices) - 1

    faces = []

    # Faces laterais (entre anéis)
    for i in range(n_rings - 1):
        for j in range(m):
            p0 = i * m + j
            p1 = i * m + (j + 1) % m
            p2 = (i + 1) * m + j
            p3 = (i + 1) * m + (j + 1) % m
            faces.append([p0, p1, p2])
            faces.append([p1, p3, p2])

    # Tampa inferior (base)
    for j in range(m):
        v0 = base_center_index
        v1 = j
        v2 = (j + 1) % m
        faces.append([v0, v1, v2])

    # Tampa superior (topo)
    offset = (n_rings - 1) * m
    for j in range(m):
        v0 = top_center_index
        v1 = offset + (j + 1) % m
        v2 = offset + j
        faces.append([v0, v1, v2])  # sentido horário invertido

    return vertices, faces

def criar_reta(P1, P2):
  distancia = np.linalg.norm(P2 - P1)
  # Vetor direção (qualquer direção que você quiser)
  if distancia != 4:
    direcao = P2 - P1
    # Normaliza o vetor (comprimento vira 1)
    direcao_unitaria = direcao / np.linalg.norm(direcao)
    # Escala o vetor para comprimento 4
    direcao_reta = direcao_unitaria * 4
    P2 = P1+direcao_reta
  vertices = np.array([P1, P2])
  return vertices

