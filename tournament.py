def buy_cars(self):
        """Have all teams purchase their initial car inventory"""
            for team in self.teams:
                self._purchase_inventory(team)
    
        def _purchase_inventory(self, team):
        """Greedy algorithm to purchase optimal cars within budget (maximizing MPG-H)"""
            # 1. Load car data
            try:
                with open(self.car_data_path, 'r') as f:
                    # Skip header and parse CSV: Make,Model,MPG-H,Price
                    cars = [line.strip().split(',') for line in f.readlines()[1:]] 
            except FileNotFoundError:
                raise FileNotFoundError(f"Car data file {self.car_data_path} not found")

            # 2. Filter cars by team's sponsor and convert to numeric
            available_cars = []
            for make, model, mpg, price in cars:
                if make == team.sponsor:
                    try:
                        available_cars.append({
                            'model': model,
                            'mpg': float(mpg),
                            'price': float(price)
                        })
                    except ValueError:
                        continue  # Skip invalid entries

            # 3. Greedy selection - sort by MPG-H descending
            available_cars.sort(key=lambda x: x['mpg'], reverse=True)

            # 4. Purchase cars until budget exhausted
            team.inventory = []
            remaining_budget = team.budget
    
            for car in available_cars:
                if car['price'] <= remaining_budget:
                    team.inventory.append({
                        'model': car['model'],
                        'mpg': car['mpg']
                    })
                    remaining_budget -= car['price']
                    # Optional: uncomment for debugging
                    # print(f"Purchased {car['model']} (MPG: {car['mpg']}, Price: {car['price']})") 

            # 5. Update team's remaining budget
            team.budget = remaining_budget Is the greedy algorithm here a good idea? Is it simple enough to understand and implement?
    

        def hold_event(self):
            """Run the tournament competition process"""
            if not self.teams:
                raise ValueError("No teams available for tournament")
    
            # Make a copy of active teams for the tournament
            active_teams = [team for team in self.teams if team.active]
    
            # Ensure number of teams is power of 2 (should already be validated in __init__)
            if len(active_teams) == 0:
                raise ValueError("No active teams to compete")
    
            # Tournament loop until only one champion remains
            while len(active_teams) > 1:
                next_round = []
        
            # Process matches in pairs
            for i in range(0, len(active_teams), 2):
                if i+1 >= len(active_teams):
                    # Handle odd number of teams (shouldn't happen with power of 2)
                    next_round.append(active_teams[i])
                    continue
            
                team1 = active_teams[i]
                team2 = active_teams[i+1]
            
                # Run the match
                winner = self._run_match(team1, team2)
                loser = team2 if winner == team1 else team1
            
                # Update records
                winner.wins += 1
                loser.losses += 1
                loser.active = False
            
                # Award prize money
                winner.budget += 50000
            
                # Allow winner to purchase more inventory
                self._purchase_inventory(winner)
            
                # Advance winner to next round
                next_round.append(winner)
        
            active_teams = next_round
    
        # Set the champion
        if active_teams:
            self.champion = active_teams[0]
            self.champion.active = True  # Ensure champion is marked active
    
        return self.champion

        def _run_match(self, team1, team2):
            """Determine winner of a head-to-head match between two teams"""
            if not team1.inventory or not team2.inventory:
            # Edge case: if a team has no cars, they automatically lose
                return team2 if not team1.inventory else team1
    
            # Calculate team scores based on their car inventories
            score1 = sum(car['mpg'] for car in team1.inventory)
            score2 = sum(car['mpg'] for car in team2.inventory)
    
            # Store scores for tracking
            team1.scores.append(score1)
            team2.scores.append(score2)
    
            # Determine winner (higher total MPG wins)
            if score1 > score2:
                return team1
            elif score2 > score1:
                return team2
            else:
            # Tiebreaker: random choice
                return random.choice([team1, team2])
        
