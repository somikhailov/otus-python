# hw2

## Usage

```bash
docker-compose up -d --build
```
test until patch
```bash
docker-compose exec centos7-cpython-until ./python /opt/test/until.py
```

test new opcode patch
```bash
docker-compose exec centos7-cpython-new-opcode ./python /opt/test/new-opcode.py
```

test inc patch
```bash
docker-compose exec centos7-cpython-inc ./python /opt/test/inc.py
```

## License
[MIT](https://choosealicense.com/licenses/mit/)