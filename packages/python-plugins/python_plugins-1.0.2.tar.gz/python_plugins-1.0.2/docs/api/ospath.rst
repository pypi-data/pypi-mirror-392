============
ospath
============

.. code-block:: python

    from  python_plugins.ospath.walk_remove import remove
    from  python_plugins.ospath.walk_remove import remove_pycache
    from  python_plugins.ospath.walk_remove import remove_ipynb_checkpoints

    remove(dir_path,rm_dir_name)
    
    remove_pycache()   # default is "."
    remove_pycache("./tests")
    remove_ipynb_checkpoints()  # default is "."
    

    