"""Extension Cython pour accélérer la mise à jour des positions de véhicules."""

from cython cimport Py_ssize_t


def update_positions(list positions, list vitesses, double delta_t):
    cdef Py_ssize_t taille = len(positions)
    cdef Py_ssize_t index
    cdef double position
    cdef double vitesse
    cdef list resultat = [0.0] * taille

    for index in range(taille):
        position = positions[index]
        vitesse = vitesses[index]
        resultat[index] = position + vitesse * delta_t

    return resultat

