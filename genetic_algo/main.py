import random
import math

# Define the data structures for Activities, Rooms, Facilitators, and Timeslots
class Activity:
    def __init__(self, name, expected_enrollment, preferred_facilitators, other_facilitators):
        self.name = name
        self.expected_enrollment = expected_enrollment
        self.preferred_facilitators = preferred_facilitators
        self.other_facilitators = other_facilitators
        self.room = None
        self.facilitator = None
        self.timeslot = None

class Room:
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity

class Facilitator:
    def __init__(self, name):
        self.name = name
        self.activities = []

class Timeslot:
    def __init__(self, time):
        self.time = time

# Initialize activities, rooms, facilitators, and timeslots
activities = [
    Activity("SLA100A", 50, ["Glen", "Lock", "Banks", "Zeldin"], ["Numen", "Richards"]),
    Activity("SLA100B", 50, ["Glen", "Lock", "Banks", "Zeldin"], ["Numen", "Richards"]),
]

rooms = [
    Room("Slater 003", 45),
    Room("Roman 216", 30),
    Room("Loft 206", 75),
]

facilitators = [
    Facilitator("Lock"),
    Facilitator("Glen"),
    Facilitator("Banks"),
]

timeslots = [
    Timeslot("10 AM"),
    Timeslot("11 AM"),
    Timeslot("12 PM"),
]

# Initialize population size, generations, and mutation rate
population_size = 500
num_generations = 100
mutation_rate = 0.01

# Define the fitness function
def calculate_fitness(schedule):
    fitness = 0

    def overlap(activity1, activity2):
        return (
            activity1.timeslot == activity2.timeslot and
            activity1.room == activity2.room
        )

    for activity in schedule:
        activity_fitness = 0

        # Rule 1: Check if activities are scheduled at the same time and room
        same_time_room = [act for act in schedule if overlap(activity, act) and act != activity]
        if same_time_room:
            activity_fitness -= 0.5

        # Rule 2: Room size
        room_capacity = activity.room.capacity
        if room_capacity < activity.expected_enrollment:
            activity_fitness -= 0.5
        elif room_capacity > 3 * activity.expected_enrollment:
            activity_fitness -= 0.2
        elif room_capacity > 6 * activity.expected_enrollment:
            activity_fitness -= 0.4
        else:
            activity_fitness += 0.3

        # Rule 3: Facilitator assignment
        if activity.facilitator.name in activity.preferred_facilitators:
            activity_fitness += 0.5
        elif activity.facilitator.name in activity.other_facilitators:
            activity_fitness += 0.2
        else:
            activity_fitness -= 0.1

        # Rule 4: Facilitator load
        activities_in_timeslot = [act for act in schedule if overlap(activity, act) and act.facilitator == activity.facilitator]
        total_activities = len(activities_in_timeslot)
        if total_activities == 1:
            activity_fitness += 0.2
        elif total_activities > 1:
            activity_fitness -= 0.2

        if total_activities > 4:
            activity_fitness -= 0.5
        elif total_activities in (1, 2) and activity.facilitator.name != "Dr. Tyler":
            activity_fitness -= 0.4

        # Apply activity-specific adjustments (you need to implement these rules)

        # Add the activity's fitness to the overall fitness
        fitness += activity_fitness

    return fitness


# Generate the initial population
def generate_initial_population():
    population = []
    for _ in range(population_size):
        schedule = randomize_schedule()
        population.append(schedule)
    return population

# Randomly initialize a schedule
def randomize_schedule():
    schedule = []
    for activity in activities:
        room = random.choice(rooms)
        facilitator = random.choice(facilitators)
        timeslot = random.choice(timeslots)
        activity.room = room
        activity.facilitator = facilitator
        activity.timeslot = timeslot
        room.capacity -= activity.expected_enrollment
        facilitator.activities.append(activity)
        schedule.append(activity)
    return schedule

# Select pairs for reproduction based on fitness
def select_parents(population, num_parents):
    parents = random.choices(population, k=num_parents)
    parents.sort(key=lambda x: calculate_fitness(x))
    return parents

# Create offspring using crossover
def crossover(parent1, parent2):
    offspring1 = []
    offspring2 = []

    crossover_point = random.randint(0, len(parent1))

    for i in range(len(parent1)):
        if i < crossover_point:
            offspring1.append(parent1[i])
            offspring2.append(parent2[i])
        else:
            offspring1.append(parent2[i])
            offspring2.append(parent1[i])

    return offspring1, offspring2

# Apply mutation to a schedule
def mutate(schedule):
    for activity in schedule:
        if random.random() < mutation_rate:
            mutation_type = random.choice(["room", "facilitator", "timeslot"])

            if mutation_type == "room":
                new_room = random.choice(rooms)
                while new_room == activity.room:
                    new_room = random.choice(rooms)
                activity.room.capacity += activity.expected_enrollment
                activity.room = new_room
                new_room.capacity -= activity.expected_enrollment

            elif mutation_type == "facilitator":
                new_facilitator = random.choice(facilitators)
                while new_facilitator == activity.facilitator:
                    new_facilitator = random.choice(facilitators)
                activity.facilitator.activities.remove(activity)
                activity.facilitator = new_facilitator
                new_facilitator.activities.append(activity)

            else:
                # Mutate the timeslot assignment
                new_timeslot = random.choice(timeslots)
                while new_timeslot == activity.timeslot:
                    new_timeslot = random.choice(timeslots)
                activity.timeslot = new_timeslot

# Main genetic algorithm loop
def genetic_algorithm():
    population = generate_initial_population()
    for generation in range(num_generations):
        new_population = []
        for _ in range(population_size // 2):
            parent1, parent2 = select_parents(population, 2)
            offspring1, offspring2 = crossover(parent1, parent2)
            mutate(offspring1)
            mutate(offspring2)
            new_population.extend([offspring1, offspring2])
        population = new_population

    best_schedule = min(population, key=calculate_fitness)
    best_fitness = calculate_fitness(best_schedule)
    print("Best Fitness:", best_fitness)

    with open("final_schedule.txt", "w") as f:
        for activity in best_schedule:
            f.write(f"{activity.name}: Room - {activity.room.name}, "
                    f"Facilitator - {activity.facilitator.name}, Time - {activity.timeslot.time}\n")

if __name__ == "__main__":
    genetic_algorithm()
