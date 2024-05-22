using Microsoft.Maui.Handlers;
using Microsoft.Maui.Platform;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using WColor = Windows.UI.Color;

namespace WMiIApp.Handlers
{
    public partial class SearchBarExHandler : SearchBarHandler
    {
        public void SetIconColor(WColor value)
        {
            PlatformView.QueryIcon.Foreground = new Microsoft.UI.Xaml.Media.SolidColorBrush(value);
        }

        private WColor GetTextColor() => VirtualView.TextColor.ToWindowsColor();

        public static void MapIconColor(ISearchBarHandler handler, ISearchBar searchBar)
        {
            if (handler is SearchBarExHandler customHandler)
                customHandler.SetIconColor(customHandler.GetTextColor());
        }
    }
}
