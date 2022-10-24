## Docker setup
```bash
docker run -dt --name d4j-cov -v $(pwd)/workspace:/root/workspace -v $(pwd)/coverage:/root/coverage agb94/d4j:latest
docker exec -it d4j-cov bash
```

## Measuring coverage
```bash
sh measure_coverage.sh <pid> <vid>b
# ex) sh measure_coverage.sh Lang 65b
```
This command will measure the coverage of `<pid>-<vid>b` in Defects4J using Cobertura and save the coverage matrix into `./coverage/<pid>-<vid>b.pkl`.

```python
import pandas as pd
df = pd.read_pickle('./coverage/<pid>-<vid>b.pkl')
# ex) pd.read_pickle('./coverage/Lang-65b.pkl')
```
