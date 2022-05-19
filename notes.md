
# runtimes:
run using all_files_by_extension_git:
```
Results obtained in:12.364801168441772 seconds
Contributor total lines: 686
defaultdict(<class 'int'>,
            {'Alex Smith': 2,
             'GitHub': 1,
             'Michael Meyer': 8,
             'Pasi Kallinen': 105,
             'PatR': 345,
             'Patric Mueller': 10,
             'SHIRAKATA Kentaro': 17,
             'copperwater': 10,
             'nhkeni': 55,
             'nhmall': 133})
```

run run using all_files_by_extension:
```text
Results obtained in:12.35106372833252 seconds
Contributor total lines: 686
defaultdict(<class 'int'>,
            {'Alex Smith': 2,
             'GitHub': 1,
             'Michael Meyer': 8,
             'Pasi Kallinen': 105,
             'PatR': 345,
             'Patric Mueller': 10,
             'SHIRAKATA Kentaro': 17,
             'copperwater': 10,
             'nhkeni': 55,
             'nhmall': 133})
```

Async version
```text
Results obtained in:3.9284491539001465 seconds
Contributor total lines: 383393
Counter({'Pasi Kallinen': 352400,
         'PatR': 14823,
         'nhmall': 14623,
         'nhkeni': 1084,
         'Patric Mueller': 198,
         'SHIRAKATA Kentaro': 188,
         'copperwater': 35,
         'Michael Meyer': 25,
         'Alex Smith': 14,
         'GitHub': 3})

```
