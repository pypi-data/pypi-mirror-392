using System;
using System.Runtime.InteropServices;
using System.Windows.Forms;

namespace AlyiosDialogHelper
{
    class Program
    {
        [DllImport("user32.dll")]
        static extern bool SetProcessDPIAware();

        [STAThread]
        static int Main(string[] args)
        {
            // Enable DPI awareness immediately
            SetProcessDPIAware();
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            if (args.Length < 1)
            {
                Console.Error.WriteLine("Usage: DialogHelper <type> [options]");
                return 1;
            }

            string dialogType = args[0].ToLower();

            try
            {
                switch (dialogType)
                {
                    case "openfile":
                        return OpenFileDialog(args);
                    case "savefile":
                        return SaveFileDialog(args);
                    case "folder":
                        return FolderDialog(args);
                    default:
                        Console.Error.WriteLine("Unknown dialog type: " + dialogType);
                        return 1;
                }
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("Error: " + ex.Message);
                return 1;
            }
        }

        static int OpenFileDialog(string[] args)
        {
            using (var dialog = new OpenFileDialog())
            {
                dialog.AutoUpgradeEnabled = true;
                dialog.CheckFileExists = true;
                dialog.CheckPathExists = true;
                dialog.DereferenceLinks = true;
                dialog.RestoreDirectory = true;

                // Parse arguments
                for (int i = 1; i < args.Length; i++)
                {
                    string arg = args[i];
                    if (arg.StartsWith("--title="))
                    {
                        dialog.Title = arg.Substring(8);
                    }
                    else if (arg.StartsWith("--initialdir="))
                    {
                        dialog.InitialDirectory = arg.Substring(13);
                    }
                    else if (arg.StartsWith("--filter="))
                    {
                        dialog.Filter = arg.Substring(9);
                    }
                    else if (arg == "--multiple")
                    {
                        dialog.Multiselect = true;
                    }
                }

                if (dialog.ShowDialog() == DialogResult.OK)
                {
                    if (dialog.Multiselect)
                    {
                        Console.WriteLine(string.Join("|", dialog.FileNames));
                    }
                    else
                    {
                        Console.WriteLine(dialog.FileName);
                    }
                    return 0;
                }
                return 2; // Cancelled
            }
        }

        static int SaveFileDialog(string[] args)
        {
            using (var dialog = new SaveFileDialog())
            {
                dialog.AutoUpgradeEnabled = true;
                dialog.CheckPathExists = true;
                dialog.DereferenceLinks = true;
                dialog.RestoreDirectory = true;
                dialog.OverwritePrompt = true;

                // Parse arguments
                for (int i = 1; i < args.Length; i++)
                {
                    string arg = args[i];
                    if (arg.StartsWith("--title="))
                    {
                        dialog.Title = arg.Substring(8);
                    }
                    else if (arg.StartsWith("--initialdir="))
                    {
                        dialog.InitialDirectory = arg.Substring(13);
                    }
                    else if (arg.StartsWith("--filename="))
                    {
                        dialog.FileName = arg.Substring(11);
                    }
                    else if (arg.StartsWith("--defaultext="))
                    {
                        dialog.DefaultExt = arg.Substring(13);
                    }
                    else if (arg.StartsWith("--filter="))
                    {
                        dialog.Filter = arg.Substring(9);
                    }
                }

                if (dialog.ShowDialog() == DialogResult.OK)
                {
                    Console.WriteLine(dialog.FileName);
                    return 0;
                }
                return 2; // Cancelled
            }
        }

        static int FolderDialog(string[] args)
        {
            using (var dialog = new FolderBrowserDialog())
            {
                dialog.ShowNewFolderButton = true;

                // Parse arguments
                for (int i = 1; i < args.Length; i++)
                {
                    string arg = args[i];
                    if (arg.StartsWith("--description="))
                    {
                        dialog.Description = arg.Substring(14);
                    }
                    else if (arg.StartsWith("--selectedpath="))
                    {
                        dialog.SelectedPath = arg.Substring(15);
                    }
                }

                if (dialog.ShowDialog() == DialogResult.OK)
                {
                    Console.WriteLine(dialog.SelectedPath);
                    return 0;
                }
                return 2; // Cancelled
            }
        }
    }
}
