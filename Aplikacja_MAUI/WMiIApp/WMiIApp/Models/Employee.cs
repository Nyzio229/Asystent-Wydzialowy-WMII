using CommunityToolkit.Mvvm.ComponentModel;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace WMiIApp.Models
{
    public partial class Employee : ObservableObject
    {
        [field: NonSerialized]
        public string name;
        [JsonProperty("name")]
        public string Name { get => name; set => SetProperty(ref name, value); }

        [field: NonSerialized]
        public string office;
        [JsonProperty("office")]
        public string Office { get => office; set => SetProperty(ref office, value); }

        [field: NonSerialized]
        public bool isWorking;
        [JsonProperty("isWorking")]
        public bool IsWorking { get => isWorking; set => SetProperty(ref isWorking, value); }
    }
}
