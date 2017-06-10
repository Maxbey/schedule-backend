release:
	docker tag schedulebackend_web maxbey/schedule-backend
	docker push maxbey/schedule-backend
test:
	(cd schedule;coverage run ./manage.py test --nologcapture;coverage report)
localserver:
	docker-compose build
	docker-compose up -d db
	sleep 5
	docker-compose up -d nginx
