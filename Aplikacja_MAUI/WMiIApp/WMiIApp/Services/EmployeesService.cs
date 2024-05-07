using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using WMiIApp.Models;

namespace WMiIApp.Services
{
    static public class EmployeesService
    {
        //const string uri = "https://13ad-188-146-252-197.ngrok-free.app/";
        //const string uriMain = uri + "Employees";
        const string uriMain = "https://kamilficerman.github.io/sth.json";
        static HttpClient httpClient = new();

        async static public Task<ObservableCollection<Employee>> GetEmployees()
        {
            var response = await httpClient.GetAsync(uriMain);
            response.EnsureSuccessStatusCode();
            var responseContent = await response.Content.ReadAsStringAsync();
            var list = JsonConvert.DeserializeObject<ObservableCollection<Employee>>(responseContent);
            return list;
        }
    }
}
