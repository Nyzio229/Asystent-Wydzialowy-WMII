using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace WMiIApp.Models
{
    public class TableContext
    {
        public int id_pytania { get; set; }
        public string? pytanie { get; set; }
        public string? odpowiedz { get; set; }
    }
}
