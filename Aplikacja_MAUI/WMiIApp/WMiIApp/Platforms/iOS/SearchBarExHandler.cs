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
#if IOS13_0_OR_GREATER
            var textField = PlatformView.SearchTextField;
            var leftView = textField.LeftView ?? throw new Exception();
            leftView.TintColor = value;
#endif
        }

        private UIColor GetTextColor() => VirtualView.TextColor.ToPlatform();

        public static void MapIconColor(ISearchBarHandler handler, ISearchBar searchBar)
        {
            if (handler is SearchBarExHandler customHandler)
                customHandler.SetIconColor(customHandler.GetTextColor());
        }
    }
}
