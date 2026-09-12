"""Distinct city silhouettes used behind discoverable food markers."""

import math

from ..config import linear_gradient, rgb


FOOD_POSITIONS = {
    'beijing': ((.28, .38), (.72, .51)),
    'tianjin': ((.27, .52), (.72, .38)),
    'yangzhou': ((.28, .38), (.71, .55)),
    'suzhou': ((.27, .54), (.72, .38)),
    'hangzhou': ((.28, .40), (.70, .54)),
}


def _water(phase: float) -> list:
    shimmer = .004 * math.sin(phase * 1.8)
    data = [
        ['R', [.065, .205, .87, .17], {'fill': rgb(174, 207, 204)}],
        ['B', [[.08, .31 + shimmer], [.31, .34 - shimmer], [.63, .28 + shimmer], [.92, .32]],
         {'stroke': rgb(222, 236, 225), 'stroke_width': 2}],
        ['B', [[.12, .25 - shimmer], [.36, .28 + shimmer], [.67, .23], [.88, .27 + shimmer]],
         {'stroke': rgb(131, 177, 180), 'stroke_width': 2}],
    ]
    return data


def _beijing(theme, phase):
    roof = rgb(137, 48, 39)
    gold = rgb(202, 159, 62)
    return [
        ['R', [.18, .35, .64, .16], {'fill': rgb(174, 72, 54), 'stroke': rgb(105, 52, 39), 'stroke_width': 2}],
        ['R', [.25, .51, .50, .11], {'fill': rgb(190, 79, 54), 'stroke': rgb(105, 52, 39), 'stroke_width': 2}],
        ['G', [[.20,.51],[.80,.51],[.73,.59],[.27,.59]], {'fill': roof, 'stroke': gold, 'stroke_width': 2}],
        ['G', [[.27,.62],[.73,.62],[.67,.69],[.33,.69]], {'fill': roof, 'stroke': gold, 'stroke_width': 2}],
        ['R', [.45,.35,.10,.18], {'fill': rgb(76, 49, 37)}],
        ['C', [.50,.61,.018], {'fill': gold}],
    ]


def _tianjin(theme, phase):
    steel = rgb(69, 91, 103)
    spokes = []
    for index in range(12):
        angle = math.tau * index / 12 + phase * .08
        spokes.append(['L', [[.70,.53],[.70 + .105*math.cos(angle), .53 + .105*math.sin(angle)]],
                       {'stroke': rgb(116, 139, 145), 'stroke_width': 1}])
    return [
        ['A', [.70,.53,.11,0,360], {'stroke': steel, 'stroke_width': 4}],
        *spokes,
        ['L', [[.59,.36],[.70,.53],[.81,.36]], {'stroke': steel, 'stroke_width': 4}],
        ['B', [[.10,.39],[.30,.50],[.48,.34],[.61,.42]], {'stroke': rgb(94, 78, 65), 'stroke_width': 7}],
        ['L', [[.14,.39],[.58,.42]], {'stroke': rgb(211, 169, 93), 'stroke_width': 2}],
    ]


def _yangzhou(theme, phase):
    willow = rgb(74, 125, 80)
    return [
        ['R', [.58,.38,.19,.12], {'fill': rgb(203, 184, 146), 'stroke': rgb(83, 71, 55), 'stroke_width': 2}],
        ['G', [[.54,.50],[.81,.50],[.73,.58],[.62,.58]], {'fill': rgb(60, 87, 77), 'stroke': rgb(184, 134, 65), 'stroke_width': 2}],
        ['L', [[.675,.58],[.675,.67]], {'stroke': rgb(80, 59, 40), 'stroke_width': 3}],
        ['G', [[.62,.67],[.73,.67],[.69,.72],[.65,.72]], {'fill': rgb(60, 87, 77)}],
        ['B', [[.12,.37],[.25,.56],[.39,.56],[.53,.37]], {'stroke': rgb(210, 203, 178), 'stroke_width': 13}],
        ['B', [[.13,.37],[.25,.52],[.39,.52],[.52,.37]], {'stroke': rgb(93, 85, 69), 'stroke_width': 2}],
        ['L', [[.19,.72],[.18,.42]], {'stroke': rgb(87, 72, 48), 'stroke_width': 5}],
        ['B', [[.19,.67],[.12,.60],[.16,.50],[.10,.42]], {'stroke': willow, 'stroke_width': 3}],
        ['B', [[.20,.64],[.28,.58],[.23,.48],[.29,.40]], {'stroke': willow, 'stroke_width': 3}],
    ]


def _suzhou(theme, phase):
    ink = rgb(61, 66, 65)
    return [
        ['R', [.12,.36,.72,.20], {'fill': rgb(239, 236, 218), 'stroke': ink, 'stroke_width': 2}],
        ['G', [[.10,.56],[.39,.56],[.34,.62],[.16,.62]], {'fill': ink}],
        ['G', [[.38,.56],[.86,.56],[.78,.64],[.48,.64]], {'fill': ink}],
        ['C', [.31,.43,.055], {'fill': ink}],
        ['R', [.255,.36,.11,.08], {'fill': ink}],
        ['B', [[.48,.36],[.59,.55],[.72,.55],[.84,.36]], {'stroke': rgb(223, 218, 196), 'stroke_width': 17}],
        ['B', [[.48,.36],[.59,.52],[.72,.52],[.84,.36]], {'stroke': ink, 'stroke_width': 2}],
        ['L', [[.18,.48],[.25,.48]], {'stroke': rgb(142, 73, 53), 'stroke_width': 3}],
    ]


def _hangzhou(theme, phase):
    hill = rgb(93, 132, 94)
    return [
        ['B', [[.08,.39],[.22,.64],[.38,.48],[.53,.61]], {'stroke': rgb(140, 163, 121), 'stroke_width': 36}],
        ['B', [[.42,.42],[.58,.65],[.74,.49],[.92,.59]], {'stroke': hill, 'stroke_width': 40}],
        ['R', [.64,.38,.10,.22], {'fill': rgb(196, 170, 112), 'stroke': rgb(85, 67, 49), 'stroke_width': 2}],
        ['G', [[.61,.60],[.77,.60],[.73,.65],[.65,.65]], {'fill': rgb(103, 74, 50)}],
        ['G', [[.62,.53],[.76,.53],[.73,.58],[.65,.58]], {'fill': rgb(103, 74, 50)}],
        ['G', [[.63,.46],[.75,.46],[.72,.51],[.66,.51]], {'fill': rgb(103, 74, 50)}],
        ['C', [.18,.62,.034], {'fill': rgb(231, 188, 101)}],
    ]


SCENE_BUILDERS = {
    'beijing': _beijing,
    'tianjin': _tianjin,
    'yangzhou': _yangzhou,
    'suzhou': _suzhou,
    'hangzhou': _hangzhou,
}


def get_city_scene(city_id: str, theme, phase: float, gradient_steps: int = 12) -> list:
    data = [
        ['RR', [.06,.20,.88,.59,.030], {'fill': rgb(235, 226, 200), 'stroke': theme, 'stroke_width': 2}],
        ['R', [.065,.375,.87,.41], {'gradient': linear_gradient([
            [rgb(224, 232, 218), 0.0], [rgb(244, 225, 191), .62], [rgb(234, 210, 174), 1.0],
        ], angle=90, steps=gradient_steps)}],
    ]
    data.extend(_water(phase))
    data.extend(SCENE_BUILDERS[city_id](theme, phase))
    return data
