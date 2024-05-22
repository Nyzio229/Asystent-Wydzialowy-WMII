using Microsoft.Maui.Handlers;
using Microsoft.Maui.Platform;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using UIKit;

namespace WMiIApp.Handlers
{
    public partial class SearchBarExHandler : SearchBarHandler
    {
        public void SetIconColor(UIColor value)
        {
            //unimplemented
            throw new NotImplementedException();
        }

        private UIColor GetTextColor() => VirtualView.TextColor.ToPlatform();

        public static void MapIconColor(ISearchBarHandler handler, ISearchBar searchBar)
        {
            if (handler is SearchBarExHandler customHandler)
                customHandler.SetIconColor(customHandler.GetTextColor());
        }
    }
}
