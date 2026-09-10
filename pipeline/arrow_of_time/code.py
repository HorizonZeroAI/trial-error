import random
import math
import json
import statistics
from collections import defaultdict

def simulate_2d_gas(n_particles, box_size, n_steps, coarse_grid_size):
    """Simulate 2D ideal gas with coarse-grained entropy tracking"""
    # Initialize particles in one quadrant (low entropy state)
    particles = []
    for i in range(n_particles):
        x = random.uniform(0, box_size/2)
        y = random.uniform(0, box_size/2)
        vx = random.gauss(0, 1)
        vy = random.gauss(0, 1)
        particles.append([x, y, vx, vy])
    
    entropies = []
    trajectories = []
    
    for step in range(n_steps):
        # Simple ballistic motion (no collisions for simplicity)
        for p in particles:
            p[0] += p[2] * 0.01  # x += vx * dt
            p[1] += p[3] * 0.01  # y += vy * dt
            
            # Periodic boundary conditions
            p[0] = p[0] % box_size
            p[1] = p[1] % box_size
        
        # Calculate coarse-grained entropy
        entropy = calculate_coarse_entropy(particles, box_size, coarse_grid_size)
        entropies.append(entropy)
        
        # Store trajectory snapshot every 10 steps
        if step % 10 == 0:
            snapshot = [[p[0], p[1]] for p in particles]
            trajectories.append(snapshot)
    
    return entropies, trajectories, particles

def calculate_coarse_entropy(particles, box_size, grid_size):
    """Calculate Boltzmann entropy from coarse-grained distribution"""
    cell_counts = defaultdict(int)
    cell_size = box_size / grid_size
    
    for p in particles:
        cell_x = int(p[0] / cell_size)
        cell_y = int(p[1] / cell_size)
        cell_counts[(cell_x, cell_y)] += 1
    
    n_total = len(particles)
    entropy = 0.0
    
    for count in cell_counts.values():
        if count > 0:
            prob = count / n_total
            entropy -= prob * math.log(prob)
    
    return entropy

def time_reverse_trajectory(particles):
    """Reverse velocities for time-reversal experiment"""
    reversed_particles = []
    for p in particles:
        reversed_particles.append([p[0], p[1], -p[2], -p[3]])
    return reversed_particles

def compute_entropy_production_stats(entropies, window_size=5):
    """Compute entropy production statistics"""
    productions = []
    for i in range(len(entropies) - window_size):
        delta_s = entropies[i + window_size] - entropies[i]
        productions.append(delta_s)
    
    positive_count = sum(1 for ds in productions if ds > 0)
    negative_count = sum(1 for ds in productions if ds < 0)
    
    return positive_count, negative_count, productions

def simple_ml_classifier(forward_clips, reversed_clips):
    """Simple entropy-based classifier for time direction"""
    correct_predictions = 0
    total_predictions = 0
    
    # Feature: entropy trend (increasing = forward, decreasing = reversed)
    for clip in forward_clips:
        entropy_trend = clip[-1] - clip[0]  # Final - initial entropy
        prediction = entropy_trend > 0  # Predict forward if entropy increases
        correct_predictions += int(prediction)
        total_predictions += 1
    
    for clip in reversed_clips:
        entropy_trend = clip[-1] - clip[0]
        prediction = entropy_trend <= 0  # Predict reversed if entropy decreases
        correct_predictions += int(prediction)
        total_predictions += 1
    
    return correct_predictions / total_predictions if total_predictions > 0 else 0.5

def main_experiment():
    """Main experiment combining all components"""
    n_particles = 200
    box_size = 10.0
    n_steps = 100
    coarse_grid_size = 4
    
    # Forward simulation
    forward_entropies, forward_traj, final_particles = simulate_2d_gas(
        n_particles, box_size, n_steps, coarse_grid_size)
    
    # Time-reversed simulation
    reversed_particles = time_reverse_trajectory(final_particles)
    reversed_entropies, reversed_traj, _ = simulate_2d_gas_from_state(
        reversed_particles, box_size, n_steps, coarse_grid_size)
    
    # Entropy production analysis
    pos_count, neg_count, productions = compute_entropy_production_stats(forward_entropies)
    
    # Fluctuation theorem test
    if neg_count > 0:
        ratio = pos_count / neg_count
        expected_ratio = math.exp(statistics.mean([p for p in productions if p > 0]))
        fluctuation_agreement = abs(ratio - expected_ratio) / expected_ratio < 0.2
    else:
        fluctuation_agreement = True
    
    # ML classification test
    clip_length = 10
    forward_clips = [forward_entropies[i:i+clip_length] 
                    for i in range(0, len(forward_entropies)-clip_length, 5)]
    reversed_clips = [reversed_entropies[i:i+clip_length] 
                     for i in range(0, len(reversed_entropies)-clip_length, 5)]
    
    ml_accuracy = simple_ml_classifier(forward_clips, reversed_clips)
    
    # Overall assessment
    entropy_increases = forward_entropies[-1] > forward_entropies[0]
    arrow_detected = ml_accuracy > 0.6
    
    success = entropy_increases and arrow_detected and fluctuation_agreement
    evidence = f"Entropy increase: {entropy_increases}, ML accuracy: {ml_accuracy:.3f}, Fluctuation test: {fluctuation_agreement}"
    
    return success, evidence, ml_accuracy

def simulate_2d_gas_from_state(particles, box_size, n_steps, coarse_grid_size):
    """Continue simulation from given particle state"""
    entropies = []
    trajectories = []
    
    for step in range(n_steps):
        for p in particles:
            p[0] += p[2] * 0.01
            p[1] += p[3] * 0.01
            p[0] = p[0] % box_size
            p[1] = p[1] % box_size
        
        entropy = calculate_coarse_entropy(particles, box_size, coarse_grid_size)
        entropies.append(entropy)
        
        if step % 10 == 0:
            snapshot = [[p[0], p[1]] for p in particles]
            trajectories.append(snapshot)
    
    return entropies, trajectories, particles

# Run experiment
success, evidence, metric = main_experiment()
print(json.dumps({"pass": success, "evidence": evidence, "metric": metric}))