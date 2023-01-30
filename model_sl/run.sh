docker run \
	-d \
	--restart always \
	--name anonimizator-api \
	-p 5006:4000 \
	--mount type=bind,source="`pwd`/models/bert-anon-v1/",destination="/app/models/bert-anon-v1/",ro \
	anonimizator-api:v1