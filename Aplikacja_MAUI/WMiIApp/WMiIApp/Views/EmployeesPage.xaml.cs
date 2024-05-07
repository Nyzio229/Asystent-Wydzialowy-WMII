using System.Diagnostics;
using WMiIApp.ViewModels;

namespace WMiIApp;

public partial class EmployeesPage : ContentPage
{
	public EmployeesPage(EmployeesViewModel vm)
	{

		InitializeComponent();
		BindingContext = vm;
	}
}