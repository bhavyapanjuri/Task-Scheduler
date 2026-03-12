from collections import Counter, deque
import heapq

class TaskScheduler:
    def __init__(self, tasks, cooldown, cores=1):
        self.tasks = tasks
        self.cooldown = cooldown
        self.cores = cores
        self.timeline = []
        
    def calculate_min_time(self):
        """Calculate minimum time needed to complete all tasks"""
        if not self.tasks:
            return 0
        
        freq = Counter(self.tasks)
        max_freq = max(freq.values())
        max_count = sum(1 for f in freq.values() if f == max_freq)
        
        # Formula: (max_freq - 1) * (cooldown + 1) + max_count
        min_time = (max_freq - 1) * (self.cooldown + 1) + max_count
        return max(min_time, len(self.tasks))
    
    def execute_single_core(self):
        """Execute tasks on single core with cooldown"""
        if not self.tasks:
            return []
        
        freq = Counter(self.tasks)
        max_heap = [(-count, task) for task, count in freq.items()]
        heapq.heapify(max_heap)
        
        timeline = []
        cooldown_queue = deque()
        time = 0
        
        while max_heap or cooldown_queue:
            # Move tasks from cooldown back to heap
            if cooldown_queue and cooldown_queue[0][0] <= time:
                _, task, count = cooldown_queue.popleft()
                heapq.heappush(max_heap, (-count, task))
            
            if max_heap:
                count, task = heapq.heappop(max_heap)
                count = -count
                timeline.append((time, task))
                
                # Add to cooldown if more executions needed
                if count > 1:
                    cooldown_queue.append((time + self.cooldown + 1, task, count - 1))
                time += 1
            else:
                # Idle - jump to next available task
                if cooldown_queue:
                    next_time = cooldown_queue[0][0]
                    timeline.append((time, 'IDLE'))
                    time = next_time
        
        return timeline
    
    def execute_multi_core(self):
        """Execute tasks on multiple cores"""
        if not self.tasks:
            return []
        
        freq = Counter(self.tasks)
        max_heap = [(-count, task) for task, count in freq.items()]
        heapq.heapify(max_heap)
        
        timeline = []
        cooldown_queue = deque()
        time = 0
        
        while max_heap or cooldown_queue:
            # Move tasks from cooldown back to heap
            while cooldown_queue and cooldown_queue[0][0] <= time:
                _, task, count = cooldown_queue.popleft()
                heapq.heappush(max_heap, (-count, task))
            
            # Execute on available cores
            executed = []
            for _ in range(min(self.cores, len(max_heap))):
                if max_heap:
                    count, task = heapq.heappop(max_heap)
                    count = -count
                    executed.append(task)
                    
                    if count > 1:
                        cooldown_queue.append((time + self.cooldown + 1, task, count - 1))
            
            if executed:
                timeline.append((time, executed))
                time += 1
            else:
                # All cores idle
                if cooldown_queue:
                    timeline.append((time, ['IDLE'] * self.cores))
                    time = cooldown_queue[0][0]
        
        return timeline
    
    def run(self):
        """Execute scheduler and display results"""
        print(f"\n{'='*60}")
        print(f"TASK SCHEDULER SIMULATION")
        print(f"{'='*60}")
        print(f"Tasks: {self.tasks}")
        print(f"Cooldown: {self.cooldown}")
        print(f"CPU Cores: {self.cores}")
        print(f"{'='*60}\n")
        
        # Calculate minimum time
        min_time = self.calculate_min_time()
        print(f"Minimum Time Required: {min_time} units\n")
        
        # Execute based on cores
        if self.cores == 1:
            timeline = self.execute_single_core()
            print("EXECUTION TIMELINE (Single Core):")
            print(f"{'Time':<8} {'Task':<10}")
            print("-" * 20)
            for time, task in timeline:
                print(f"{time:<8} {task:<10}")
        else:
            timeline = self.execute_multi_core()
            print(f"EXECUTION TIMELINE ({self.cores} Cores):")
            print(f"{'Time':<8} {'Tasks':<30}")
            print("-" * 40)
            for time, tasks in timeline:
                tasks_str = ', '.join(str(t) for t in tasks)
                print(f"{time:<8} {tasks_str:<30}")
        
        # Statistics
        total_time = timeline[-1][0] + 1 if timeline else 0
        idle_count = sum(1 for t in timeline if 'IDLE' in str(t[1]))
        utilization = ((total_time - idle_count) / total_time * 100) if total_time > 0 else 0
        
        print(f"\n{'='*60}")
        print(f"STATISTICS")
        print(f"{'='*60}")
        print(f"Total Execution Time: {total_time} units")
        print(f"Idle Cycles: {idle_count}")
        print(f"CPU Utilization: {utilization:.2f}%")
        print(f"{'='*60}\n")


def main():
    # Example 1: Single Core with Cooldown
    print("\n### EXAMPLE 1: Single Core ###")
    tasks1 = ['A', 'A', 'A', 'B', 'B', 'B']
    scheduler1 = TaskScheduler(tasks1, cooldown=2, cores=1)
    scheduler1.run()
    
    # Example 2: Multi-Core Execution
    print("\n### EXAMPLE 2: Multi-Core (2 Cores) ###")
    tasks2 = ['A', 'A', 'A', 'B', 'B', 'B']
    scheduler2 = TaskScheduler(tasks2, cooldown=2, cores=2)
    scheduler2.run()
    
    # Example 3: Real-time with Multiple Tasks
    print("\n### EXAMPLE 3: Complex Scheduling ###")
    tasks3 = ['A', 'A', 'A', 'A', 'B', 'B', 'C', 'C', 'D']
    scheduler3 = TaskScheduler(tasks3, cooldown=3, cores=2)
    scheduler3.run()


if __name__ == "__main__":
    main()
