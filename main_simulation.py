#Main program entry point to run the economic agent simulation 
from datetime import datetime, timezone, timedelta
import uuid
from database import SimulationDatabase
from weather import generate_next_weather
from agent import VendingMachineAgent

STARTING_BALANCE = 500
DAILY_FEE = 2

class VendingMachineSimulation:
    def __init__(self):
        self.simulation_id = str(uuid.uuid4())
        self.balance = STARTING_BALANCE
        self.inventory = {}
        # Start at 6:00 AM UTC - the daily anchor time
        now = datetime.now(timezone.utc)
        self.current_time = datetime(now.year, now.month, now.day, 6, 0, 0, tzinfo=timezone.utc)
        # Initialize counters
        self.message_count = 0
        self.days_passed = 0
        # Initialize weather
        self.current_weather = "sunny"  # Start with sunny weather
        # Initialize database
        self.db = SimulationDatabase()
        # Initialize agent
        self.agent = VendingMachineAgent("VendingBot", simulation_ref=self)
        self.log_state()

    def get_current_time(self):
        return self.current_time

    def get_day_of_week(self):
        """Get current day of the week"""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[self.current_time.weekday()]
    
    def get_month(self):
        """Get current month name"""
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        return months[self.current_time.month - 1]
    
    def log_state(self):
        """Log current state to database"""
        self.db.log_state(self.simulation_id, self.current_time, self.balance)
    
    def advance_time(self, days=0, minutes=0):
        """Advance simulation time by specified days and minutes"""
        self.current_time += timedelta(days=days, minutes=minutes)
        return self.current_time
    
    def get_day_report(self):
        """Generate comprehensive daily report for the agent"""
        day_of_week = self.get_day_of_week()
        month = self.get_month()
        day = self.current_time.day
        year = self.current_time.year
        time_str = self.current_time.strftime("%H:%M UTC")
        
        report = f"""
DAILY BUSINESS REPORT - {day_of_week}, {month} {day}, {year} at {time_str}
=================================================================

FINANCIAL STATUS:
- Current Balance: ${self.balance}
- Days in Operation: {self.days_passed}
- Daily Fee: ${DAILY_FEE}

ENVIRONMENTAL CONDITIONS:
- Weather: {self.current_weather}
- Season: {self.get_season()}

OPERATIONAL STATUS:
- Total Messages/Actions: {self.message_count}
- Simulation ID: {self.simulation_id}

INVENTORY: (Placeholder - to be implemented)
- [Inventory details will be added when vending machine integration is complete]

YESTERDAY'S SALES: (Placeholder - to be implemented)
- [Sales data will be added when sales simulation is integrated]

ACTION REQUIRED: Continue managing your vending machine business.
"""
        return report.strip()
        
    def get_season(self):
        """Get current season based on month"""
        month = self.current_time.month
        if month in [12, 1, 2]:
            return "Winter"
        elif month in [3, 4, 5]:
            return "Spring"
        elif month in [6, 7, 8]:
            return "Summer"
        else:
            return "Fall"

    def run_day(self):
        """Legacy method - advance to next day with daily updates"""
        # Advance to next day first
        self.advance_time(days=1)
        self.days_passed += 1
        
        # Generate new weather for the day
        self.current_weather = generate_next_weather(self.current_time.month, self.current_weather)
        
        self.balance = self.balance - DAILY_FEE
        self.log_state()
        print(self.get_day_report())
        
    def is_new_day_at_6am(self):
        """Check if it's 6:00 AM (daily report time)"""
        return self.current_time.hour == 6 and self.current_time.minute == 0
        
    def run_agent(self):
        """Run the agent for one action, providing daily report at 6 AM"""
        self.message_count += 1
        
        # Check if it's 6 AM (new day anchor time)
        if self.is_new_day_at_6am():
            # New day processing
            if self.message_count > 1:  # Don't increment on first run
                self.days_passed += 1
                self.balance -= DAILY_FEE
                
            # Generate weather for the new day
            self.current_weather = generate_next_weather(self.current_time.month, self.current_weather)
            
            # Get daily report for agent context
            daily_report = self.get_day_report()
            
            print(f"\n🌅 NEW DAY REPORT (Message {self.message_count})")
            print("=" * 50)
            print(daily_report)
            print("=" * 50)
            
            # Run agent with daily report as context
            response = self.agent.run_agent(context=daily_report)
            
        else:
            # Regular agent action without daily report
            response = self.agent.run_agent()
            
        print(f"\n🤖 AGENT ACTION #{self.message_count} at {self.current_time.strftime('%H:%M')}")
        print(f"Response: {response}")
        
        # Log state after each action
        self.log_state()
        
        return response


    def start_simulation(self, max_messages):
        """Run agent-driven simulation until max_messages is reached"""
        print(f"🚀 Starting Agent-Driven VendingBench Simulation")
        print(f"Simulation ID: {self.simulation_id}")
        print(f"Starting time: {self.current_time.strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"Target messages: {max_messages}")
        print("=" * 60)
        
        while self.message_count < max_messages:
            try:
                # Run agent for one action
                self.run_agent()
                
                # Early exit if we've reached message limit
                if self.message_count >= max_messages:
                    break
                    
            except KeyboardInterrupt:
                print("\n⏹️  Simulation interrupted by user")
                break
            except Exception as e:
                print(f"\n❌ Error during simulation: {e}")
                break
        
        print(f"\n🏁 SIMULATION COMPLETE")
        print(f"Final Stats: {self.message_count} messages, {self.days_passed} days, Balance: ${self.balance}")







def run_simulation():
    simulation = VendingMachineSimulation()
    
    try:
        # Test with fewer messages initially to verify the new system
        simulation.start_simulation(10)
    finally:
        simulation.db.close()


if __name__ == "__main__":
    run_simulation()