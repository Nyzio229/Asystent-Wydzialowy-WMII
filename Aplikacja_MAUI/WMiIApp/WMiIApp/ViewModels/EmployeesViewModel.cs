using CommunityToolkit.Mvvm.ComponentModel;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using WMiIApp.Services;
using WMiIApp.Models;
using CommunityToolkit.Mvvm.Input;
using CommunityToolkit.Maui.Core.Extensions;
using System.Diagnostics;

namespace WMiIApp.ViewModels
{
    public partial class EmployeesViewModel : ObservableObject
    {
        private CancellationTokenSource _cancellationTokenSource;
        [ObservableProperty]
        ObservableCollection<Employee> employees;
        [ObservableProperty]
        ObservableCollection<Employee> employeesVisible;

        public EmployeesViewModel()
        {
            Employees = [];
            EmployeesVisible = [];
            _cancellationTokenSource = new CancellationTokenSource();
            bool employeesVisibleInitialized = false;

            
            Task.Run(async () =>
            {
                while (!_cancellationTokenSource.Token.IsCancellationRequested)
                {
                    try
                    {
                        await RefreshEmployees();
                        //Employees = await EmployeesService.GetEmployees();
                        if (!employeesVisibleInitialized)
                        {
                            EmployeesVisible = Employees;
                            employeesVisibleInitialized = true;
                        }
                    }
                    catch {}
                    await Task.Delay(2000);
                }
            });

            

            //Employee emp1 = new Employee();
            //emp1.Name = "Janusz Czarny";
            //emp1.Office = "D114";
            //emp1.IsWorking = false;

            //Employee emp2 = new Employee();
            //emp2.Name = "Anna Brzoza";
            //emp2.Office = "F31";
            //emp2.IsWorking = true;

            //Employee emp3 = new Employee();
            //emp3.Name = "Kazimierz Cichociemny";
            //emp3.Office = "A2";
            //emp3.IsWorking = false;

            //Employees.Add(emp1);
            //Employees.Add(emp2);
            //Employees.Add(emp3);
            //EmployeesVisible = Employees;
        }
        static int counterToDelete = 0;
        async Task RefreshEmployees()
        {
            var newEmployees = await EmployeesService.GetEmployees();

            Employees.Clear();

            foreach (var employee in newEmployees)
            {
                Employees.Add(employee);
            }
        }

        [RelayCommand]
        void OnTextUpdated(string text)
        {
            if (!string.IsNullOrEmpty(text))
            {
                string filterText = text.ToLower();
                EmployeesVisible = Employees.Where(emp => emp.Name.ToLower().Contains(filterText)).ToObservableCollection();
            }
            else
            {
                EmployeesVisible = Employees;
            }
        }

        ~EmployeesViewModel()
        {
            _cancellationTokenSource.Cancel();
        }
    }
}
