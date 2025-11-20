// Custom Pyodide setup for pytennisscorer
async function setupPyodide(pyodide) {
  console.log('Setting up Pyodide for pytennisscorer...');

  // Install micropip for package management
  await pyodide.loadPackage('micropip');
  const micropip = pyodide.pyimport('micropip');

  // Load local pytennisscorer wheel if available
  try {
    const wheelPath = './wheels/pytennisscorer-0.1.0-py3-none-any.whl';
    await micropip.install(wheelPath);
    console.log('Loaded local pytennisscorer wheel');
  } catch (error) {
    console.warn('Could not load local wheel, will try to install from PyPI:', error);
    try {
      await micropip.install('pytennisscorer');
    } catch (pypiError) {
      console.warn('pytennisscorer not available on PyPI yet');
    }
  }

  // Pre-import common modules to speed up execution
  await pyodide.runPythonAsync(`
    # Import pytennisscorer modules
    try:
        from pytennisscorer import TennisScorer, MatchType
        from pytennisscorer.models import MatchState, SetState, GameState
        from pytennisscorer.configs import create_match_config
        print("✅ pytennisscorer loaded successfully")
    except ImportError as e:
        print(f"⚠️ Could not import pytennisscorer: {e}")
        print("You can still use the documentation, but live examples won't work")
  `);

  return pyodide;
}

// Export for Quarto-live
window.setupPyodide = setupPyodide;