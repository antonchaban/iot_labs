from app.entities.agent_data import AgentData
from app.entities.processed_agent_data import ProcessedAgentData


def process_agent_data(
        agent_data: AgentData,
) -> ProcessedAgentData:
    """
    Process agent data and classify the state of the road surface.
    Parameters:
        agent_data (AgentData): Agent data that containing accelerometer, GPS, and timestamp.
    Returns:
        processed_data_batch (ProcessedAgentData): Processed data containing the classified state of the road surface and agent data.
    """

    # Порогові значення для класифікації
    THRESHOLD_POTHOLE_Y = 1.8
    THRESHOLD_BUMP_Z = 1.5

    # Отримання значень прискорення
    ax, ay, az = agent_data.accelerometer_x, agent_data.accelerometer_y, agent_data.accelerometer_z

    # Початкові значення
    state = "normal"
    score = 0.8

    # Класифікація дорожнього стану
    if abs(ay) > THRESHOLD_POTHOLE_Y:
        state = "pothole"
        score = min(0.95, 0.7 + 0.1 * (abs(ay) / THRESHOLD_POTHOLE_Y))
    elif abs(az) > THRESHOLD_BUMP_Z:
        state = "bump"
        score = min(0.9, 0.65 + 0.1 * (abs(az) / THRESHOLD_BUMP_Z))
    else:
        max_val = max(abs(ax), abs(ay), abs(az))
        score = 0.9 - 0.1 * (max_val / min(THRESHOLD_POTHOLE_Y, THRESHOLD_BUMP_Z))

    return ProcessedAgentData(
        road_condition=state,
        confidence=score,
        location_lat=agent_data.gps_latitude,
        location_lon=agent_data.gps_longitude,
        timestamp=agent_data.timestamp,
        raw_data={
            "acceleration_x": ax,
            "acceleration_y": ay,
            "acceleration_z": az
        }
    )