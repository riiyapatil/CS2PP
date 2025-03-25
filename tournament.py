import json
import random
import csv
from tabulate import tabulate
from math import log2

class Tournament:
    """
    A tournament where teams compete based on their fuel-efficient car collections.
    
    Attributes:
        car_data_path (str): Path to car data CSV
        name (str): Tournament name
        nteams (int): Number of teams (must be power of 2)
        teams (list): List of Team objects
        champion (Team): The winning team
    """
    
    def __init__(self, config_file):
        """Initialize tournament from config (dict or JSON file path)."""
        # Load config (accepts either dict or file path)
        if isinstance(config_file, dict):
            config = config_file  # Use dict directly
        else:
            with open(config_file) as f:  # Assume it's a file path
                config = json.load(f)

        # Assign required values
        self.car_data_path = config['car_data_path']
        self.name = config['tournament_name']
        self.nteams = config.get('nteams', 16)  # Default: 16 teams

        # Validation (unchanged)
        if not isinstance(self.nteams, int):
            raise TypeError("Number of teams must be integer")
        assert self.nteams > 0, "Team count must be positive"
        assert (self.nteams & (self.nteams-1)) == 0, "Team count must be power of 2"

        # Assign optional values with defaults
        self.default_low = config.get('default_low', 20000)
        self.default_high = config.get('default_high', 50000)
        self.default_incr = config.get('default_incr', 5000)

        # Initialize empty state
        self.teams = []
        self.champion = None
    
    def __repr__(self):
        """Unambiguous representation for developers"""
        return (f"Tournament(name='{self.name}', nteams={self.nteams}, "f"car_data='{self.car_data_path}')")
    
    def __str__(self):
        """User-friendly representation"""
        return f"{self.name} Tournament with {self.nteams} teams"

    def generate_sponsors(self, sponsor_list=None, fixed_budget=None, 
                         low=None, high=None, incr=None):
        """
        Assign sponsors and budgets to all teams in the tournament.
    
        Args:
            sponsor_list: Optional list of specific sponsors (length <= nteams)
            fixed_budget: Optional fixed budget for all teams (within low/high bounds)
            low: Minimum budget value (defaults to config value)
            high: Maximum budget value (defaults to config value)
            incr: Budget increment step (defaults to config value)
        """
        # Available car manufacturers
        makers = ["Toyota", "Honda", "Ford", "Tesla", "Nissan", 
                  "BMW", "Mercedes", "Hyundai", "Kia", "Volkswagen"]
    
        # Handle sponsor list
        if sponsor_list:
            if len(sponsor_list) > self.nteams:
                raise ValueError("Sponsor list cannot exceed number of teams")
        
            # Use specified sponsors first, then fill remaining with random makers
            sponsors = sponsor_list.copy()
            remaining = self.nteams - len(sponsors)
            sponsors.extend(random.choices(makers, k=remaining))
        else:
            # Random selection with no duplicates if possible
            sponsors = random.sample(makers, min(len(makers), self.nteams))
            # If more teams than makers, allow duplicates
            if len(sponsors) < self.nteams:
                sponsors.extend(random.choices(makers, k=self.nteams - len(sponsors)))
    
        # Handle budget parameters
        low = low if low is not None else self.default_low
        high = high if high is not None else self.default_high
        incr = incr if incr is not None else self.default_incr
    
        # Generate budgets
        if fixed_budget is not None:
            if not (low <= fixed_budget <= high):
                raise ValueError(f"Fixed budget must be between {low} and {high}")
            budgets = [fixed_budget] * self.nteams
        else:
            # Create range of possible budgets and select randomly
            possible_budgets = list(range(low, high + 1, incr))
            budgets = random.choices(possible_budgets, k=self.nteams)
    
        # Store results as instance attributes
        self.team_sponsors = sponsors
        self.team_budgets = budgets
    
    def generate_teams(self):
        """Simple version without zip"""
        self.teams = []  # Start with empty list
    
        # Loop through both lists by index
        for i in range(len(self.team_sponsors)):
            sponsor = self.team_sponsors[i]
            budget = self.team_budgets[i]
            self.teams.append(self.Team(sponsor, budget))

    def buy_cars(self):
        """Have all teams purchase their initial car inventory"""
        for team in self.teams:
            self._purchase_inventory(team)

    def _purchase_inventory(self, team):
        try:
            with open(self.car_data_path, 'r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                available_cars = []
                for row in reader:
                    if row[0] == team.sponsor:
                        car = {
                            'make': row[0],
                            'model': row[1],
                            'mpg': float(row[8]),
                            'price': float(row[11])
                        }
                        if car['price'] <= team.budget:  # Only consider affordable cars
                            available_cars.append(car)
            
                # Sort by MPG descending and select top affordable cars
                available_cars.sort(key=lambda x: x['mpg'], reverse=True)
                purchased_cars = []
                total_spent = 0
            
                for car in available_cars:
                    if total_spent + car['price'] <= team.budget:
                        purchased_cars.append(car)
                        total_spent += car['price']
            
                team.inventory = purchased_cars
                team.budget -= total_spent
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Car data file {self.car_data_path} not found")

    def hold_event(self):
        """Run the tournament competition"""
        if not self.teams:
            raise ValueError("No teams available for tournament")
    
        active_teams = [team for team in self.teams if team.active]
    
        while len(active_teams) > 1:
            next_round = []
        
            for i in range(0, len(active_teams), 2):
                if i+1 >= len(active_teams):
                    next_round.append(active_teams[i])
                    continue
            
                team1 = active_teams[i]
                team2 = active_teams[i+1]
            
                winner = self._run_match(team1, team2)
                loser = team2 if winner == team1 else team1
            
                winner.wins += 1
                loser.losses += 1
                loser.active = False
                winner.budget += 50000
                self._purchase_inventory(winner)
                next_round.append(winner)
        
            active_teams = next_round
    
        if active_teams:
            self.champion = active_teams[0]
            self.champion.active = True
    
        return self.champion

    def _run_match(self, team1, team2):
        """Determine match winner"""
        if not team1.inventory:
            return team2
        if not team2.inventory:
            return team1
    
        score1 = sum(car['mpg'] for car in team1.inventory)
        score2 = sum(car['mpg'] for car in team2.inventory)
    
        team1.scores.append(score1)
        team2.scores.append(score2)
    
        if score1 > score2:
            return team1
        elif score2 > score1:
            return team2
        else:
            return random.choice([team1, team2])

    def show_win_record(self):
        """Display win/loss records for all teams in the specified format"""
        records = {}
        for team in sorted(self.teams, key=lambda x: x.sponsor):
            records[team.sponsor] = ['W     ' if w else 'L     ' 
                                   for w in ([True]*team.wins + [False]*team.losses)]
    
        # Calculate the maximum sponsor name length for alignment
        max_name_length = max(len(sponsor) for sponsor in records.keys())
    
        # Print each team's record in the desired format
        for sponsor, results in records.items():
            # Right-align the sponsor name and left-align the results
            print(f"{sponsor:>{max_name_length}}: {results}")

    def __ge__(self, x):   
        """Compare tournaments based on champions' performance (wins then losses)."""
        if not isinstance(x, Tournament):
            return NotImplemented
        # First compare wins, then losses if tied
        if self.champion.wins != x.champion.wins:
            return self.champion.wins > x.champion.wins
        return self.champion.losses < x.champion.losses


    class Team:
        """Inner class representing a competing team"""
        def __init__(self, sponsor, budget):
            self._sponsor = sponsor
            self._initial_budget = budget
            self.budget = budget
            self.inventory = []
            self.active = True
            self.wins = 0
            self.losses = 0
            self.scores = []
            self.cars_used = 0

        @property
        def sponsor(self):
            return self._sponsor

        @property
        def initial_budget(self):
            return self._initial_budget

        def __str__(self):
            status = "ACTIVE" if self.active else "ELIMINATED"
            return (f"{self.sponsor} Team: ${self.budget}, "
                    f"{len(self.inventory)} cars, "
                    f"Record: {self.wins}-{self.losses}, "
                    f"Status: {status}")

        def __repr__(self):
            return (f"Team(sponsor='{self.sponsor}', "
                    f"budget={self.budget}, "
                    f"active={self.active})")

class Tournament_optimised(Tournament):
    """Optimized tournament using 0/1 knapsack DP for car purchases"""
    
    def _purchase_inventory(self, team):
        """Purchase optimal cars using 0/1 knapsack dynamic programming"""
        try:
            with open(self.car_data_path, 'r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                cars = []
                for row in reader:
                    if row[0] == team.sponsor:
                        cars.append({
                            'make': row[0],
                            'model': row[1],
                            'mpg': float(row[8]),
                            'price': float(row[11])
                        })
                
                if not cars:
                    team.inventory = []
                    return
                
                # 0/1 Knapsack DP implementation
                budget = int(team.budget)
                n = len(cars)
                
                # DP table: rows = items, columns = budget
                dp = [[0] * (budget + 1) for _ in range(n + 1)]
                
                # Build DP table
                for i in range(1, n + 1):
                    for w in range(1, budget + 1):
                        if cars[i-1]['price'] <= w:
                            dp[i][w] = max(
                                dp[i-1][w],
                                dp[i-1][w - int(cars[i-1]['price'])] + cars[i-1]['mpg']
                            )
                        else:
                            dp[i][w] = dp[i-1][w]
                
                # Backtrack to find selected cars
                w = budget
                selected = []
                
                for i in range(n, 0, -1):
                    if dp[i][w] != dp[i-1][w]:
                        selected.append(cars[i-1])
                        w -= int(cars[i-1]['price'])
                
                team.inventory = selected
                team.budget -= sum(car['price'] for car in selected)
                
        except FileNotFoundError:
            raise FileNotFoundError(f"Car data file {self.car_data_path} not found")
