from datetime import datetime, timedelta
import random

class WorkoutExperiment:
    def __init__(self):
        self.clients = []
        self.exercises = ['Жим лежа', 'Присед', 'Становая тяга', 'Тяга штанги в наклоне', 'Жим гантелей сидя']
    
    def generate_synthetic_data(self, num_clients=50, num_workouts_per_client=20):
        """Генерация синтетических данных для эксперимента"""
        print("Генерация синтетических данных...")
        
        for client_id in range(1, num_clients + 1):
            client = {
                'id': client_id,
                'name': f'Клиент_{client_id}',
                'age': random.randint(18, 60),
                'workouts': []
            }
            
            start_date = datetime.now() - timedelta(days=num_workouts_per_client * 7)
            
            # Базовые силовые показатели для клиента
            base_strength = {ex: random.uniform(30, 100) for ex in self.exercises}
            
            for i in range(num_workouts_per_client):
                workout_date = start_date + timedelta(days=i * 7)
                exercise = random.choice(self.exercises)
                
                # Прогресс: сила увеличивается с каждой тренировкой + случайный шум
                progress_factor = 1 + (i * 0.02)
                noise = random.uniform(0.95, 1.05)
                estimated_1rm = base_strength[exercise] * progress_factor * noise
                
                training_weight = estimated_1rm * random.uniform(0.6, 0.8)
                reps = random.randint(6, 12)
                
                workout = {
                    'date': workout_date,
                    'exercise': exercise,
                    'weight_kg': round(training_weight, 1),
                    'reps': reps,
                    'estimated_1rm': round(estimated_1rm, 1)
                }
                client['workouts'].append(workout)
            
            self.clients.append(client)
        
        print(f"Сгенерировано {len(self.clients)} клиентов с {num_workouts_per_client} тренировками каждый.")

    def analyze_progress(self):
        """Анализ прогресса клиентов"""
        print("\n" + "="*60)
        print("РЕЗУЛЬТАТЫ ВЫЧИСЛИТЕЛЬНОГО ЭКСПЕРИМЕНТА")
        print("="*60)
        
        # 1. Средний прогресс по упражнениям
        print("\n1. СРЕДНИЙ ПРОГРЕСС ПО УПРАЖНЕНИЯМ:")
        for exercise in self.exercises:
            progress_data = []
            for client in self.clients:
                ex_workouts = [w for w in client['workouts'] if w['exercise'] == exercise]
                if len(ex_workouts) >= 2:
                    first_1rm = ex_workouts[0]['estimated_1rm']
                    last_1rm = ex_workouts[-1]['estimated_1rm']
                    progress = ((last_1rm - first_1rm) / first_1rm) * 100
                    progress_data.append(progress)
            
            if progress_data:
                avg_progress = sum(progress_data) / len(progress_data)
                max_progress = max(progress_data)
                min_progress = min(progress_data)
                print(f"   {exercise}:")
                print(f"     Средний: {avg_progress:.1f}% | Макс: {max_progress:.1f}% | Мин: {min_progress:.1f}%")

        # 2. Топ-5 самых результативных клиентов
        print("\n2. ТОП-5 САМЫХ РЕЗУЛЬТАТИВНЫХ КЛИЕНТОВ:")
        client_progress = []
        for client in self.clients:
            total_progress = 0
            count = 0
            for exercise in self.exercises:
                ex_workouts = [w for w in client['workouts'] if w['exercise'] == exercise]
                if len(ex_workouts) >= 2:
                    first_1rm = ex_workouts[0]['estimated_1rm']
                    last_1rm = ex_workouts[-1]['estimated_1rm']
                    progress = ((last_1rm - first_1rm) / first_1rm) * 100
                    total_progress += progress
                    count += 1
            if count > 0:
                avg_client_progress = total_progress / count
                client_progress.append((client['name'], client['age'], avg_client_progress))
        
        client_progress.sort(key=lambda x: x[2], reverse=True)
        for i, (name, age, progress) in enumerate(client_progress[:5], 1):
            print(f"   {i}. {name} (возраст: {age}): {progress:.1f}%")

        # 3. Анализ эффективности по упражнениям
        print("\n3. ЭФФЕКТИВНОСТЬ ТРЕНИРОВОК ПО УПРАЖНЕНИЯМ:")
        exercise_stats = {ex: {'progress': [], 'success_count': 0, 'total_count': 0} for ex in self.exercises}
        
        for client in self.clients:
            for exercise in self.exercises:
                ex_workouts = [w for w in client['workouts'] if w['exercise'] == exercise]
                if len(ex_workouts) >= 2:
                    first_1rm = ex_workouts[0]['estimated_1rm']
                    last_1rm = ex_workouts[-1]['estimated_1rm']
                    progress = ((last_1rm - first_1rm) / first_1rm) * 100
                    exercise_stats[exercise]['progress'].append(progress)
                    exercise_stats[exercise]['total_count'] += 1
                    if progress > 10:  # Считаем успешным прогресс более 10%
                        exercise_stats[exercise]['success_count'] += 1
        
        for exercise, stats in exercise_stats.items():
            if stats['progress']:
                avg = sum(stats['progress']) / len(stats['progress'])
                success_rate = (stats['success_count'] / stats['total_count']) * 100
                print(f"   {exercise}:")
                print(f"     Средний прогресс: {avg:.1f}%")
                print(f"     Успешность: {success_rate:.1f}%")
                print(f"     Клиентов с прогрессом: {stats['total_count']}")

        # 4. Влияние возраста на прогресс
        print("\n4. ВЛИЯНИЕ ВОЗРАСТА НА ПРОГРЕСС:")
        age_groups = {'18-30': [], '31-45': [], '46-60': []}
        
        for client in self.clients:
            total_progress = 0
            count = 0
            for exercise in self.exercises:
                ex_workouts = [w for w in client['workouts'] if w['exercise'] == exercise]
                if len(ex_workouts) >= 2:
                    first_1rm = ex_workouts[0]['estimated_1rm']
                    last_1rm = ex_workouts[-1]['estimated_1rm']
                    progress = ((last_1rm - first_1rm) / first_1rm) * 100
                    total_progress += progress
                    count += 1
            
            if count > 0:
                avg_progress = total_progress / count
                if 18 <= client['age'] <= 30:
                    age_groups['18-30'].append(avg_progress)
                elif 31 <= client['age'] <= 45:
                    age_groups['31-45'].append(avg_progress)
                else:
                    age_groups['46-60'].append(avg_progress)
        
        for group, progresses in age_groups.items():
            if progresses:
                avg = sum(progresses) / len(progresses)
                print(f"   {group} лет: средний прогресс {avg:.1f}%")

    def show_sample_data(self):
        """Показать пример данных одного клиента"""
        if not self.clients:
            print("Данные не сгенерированы.")
            return
        
        print("\n5. ДАННЫЕ ПЕРВОГО КЛИЕНТА ДЛЯ ПРИМЕРА:")
        sample_client = self.clients[0]
        print(f"   Имя: {sample_client['name']}")
        print(f"   Возраст: {sample_client['age']}")
        print("   Последние 5 тренировок:")
        
        for i, workout in enumerate(sample_client['workouts'][-5:]):
            print(f"   Тренировка {i+1}: {workout['date'].strftime('%Y-%m-%d')}")
            print(f"     Упражнение: {workout['exercise']}")
            print(f"     Рабочий вес: {workout['weight_kg']}кг")
            print(f"     Повторения: {workout['reps']}")
            print(f"     Расчетный 1ПМ: {workout['estimated_1rm']}кг")
            print()

    def run_experiment(self):
        """Запуск полного эксперимента"""
        self.generate_synthetic_data()
        self.analyze_progress()
        self.show_sample_data()

if __name__ == "__main__":
    experiment = WorkoutExperiment()
    experiment.run_experiment()
