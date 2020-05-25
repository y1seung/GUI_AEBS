import serial
import time
import numpy as np
import matplotlib.pyplot as plt
from numpy.linalg import inv
from scipy import io

W = np.array([[1, 0],
              [0, 0.1]])
dt = 0.03
w = 0.5

std_u = 0.5
Q11 = 0.5 * (dt ** 2) * std_u ** 2
Q22 = dt * std_u ** 2
Q12 = np.sqrt(Q11 * Q22)
Q21 = np.sqrt(Q11 * Q22)

A = np.array([[1, dt],
              [0, 1]])
H = np.array([[1, 0],
              [0, 1]])
Q = np.array([[Q11, Q12],
              [Q21, Q22]])
R = np.array([[0.000000022418, 0],
              [0, 0.000158449]])

x_0 = np.array([[0],
                [0]])
P_0 = 1 * np.eye(2)


def kalman_filter(z_meas, x_esti, P):
    """Kalman Filter Algorithm."""
    # (1) Prediction.
    x_pred = A @ x_esti
    P_pred = A @ P @ A.T + Q

    # (2) Kalman Gain.
    K = P_pred @ H.T @ inv(H @ P_pred @ H.T + R)

    # (3) Estimation.
    x_esti = x_pred + K @ (z_meas - H @ x_pred)

    # (4) Error Covariance.
    P = P_pred - K @ H @ P_pred

    return x_esti, P

def Kalman(pos, vel):
    x_esti, P = x_0, P_0

    z_pos = pos
    z_vel = vel

    z_meas = np.array([[z_pos], [z_vel]])

    x_esti, P = kalman_filter(z_meas, x_esti, P)

    return x_esti[0], x_esti[1]
