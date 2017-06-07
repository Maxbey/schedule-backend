release:
	docker tag schedulebackend_web maxbey/schedule-backend
	docker push maxbey/schedule-backend
test:
	(cd schedule;coverage run ./manage.py test;coverage report)
