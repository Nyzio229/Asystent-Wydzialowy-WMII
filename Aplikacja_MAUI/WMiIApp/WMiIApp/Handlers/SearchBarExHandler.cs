using Microsoft.Maui.Handlers;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace WMiIApp.Handlers
{
    public partial class SearchBarExHandler : SearchBarHandler
    {
        public static readonly IPropertyMapper<ISearchBar, SearchBarHandler> CustomMapper =
            new PropertyMapper<ISearchBar, SearchBarHandler>(Mapper)
            {
                ["IconColor"] = MapIconColor,
            };

        public SearchBarExHandler() : base(CustomMapper, CommandMapper)
        {
        }

        public override void UpdateValue(string propertyName)
        {
            base.UpdateValue(propertyName);

            if (propertyName == SearchBar.TextColorProperty.PropertyName)
            {
                SetIconColor(GetTextColor());
            }
        }
    }
}
