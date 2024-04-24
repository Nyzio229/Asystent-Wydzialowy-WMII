using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace WMiIApp.Models
{
    public class ClassifyResponse
    {
        public string label { get; set; }

        public CategoryNavigationMetadata metadata { get; set; }
    }
    public class CategoryNavigationMetadata
    {
        public string? source { get; set; }
        public string? destination { get; set; }
    }
}
