create database if not exists `shutterfly`;

USE shutterfly;

-- Create Customer Table
CREATE TABLE IF NOT EXISTS Customers (
customer_id varchar(255) NOT NULL,
event_time varchar(255) NOT NULL,
last_name varchar(255),
adr_city varchar(255),
adr_state varchar(255),
PRIMARY KEY (customer_id)
);

-- Create Site Visit Table
CREATE TABLE IF NOT EXISTS Visits(

visit_id varchar(255) NOT NULL,
event_time varchar(255) NOT NULL,
customer_id varchar(255),
tags varchar(255),
PRIMARY KEY (visit_id)
);

-- Create Image Table
CREATE TABLE IF NOT EXISTS Images(
image_id varchar(255) NOT NULL,
event_time varchar(255) NOT NULL,
customer_id varchar(255) NOT NULL,
camera_make varchar(255),
camera_model varchar(255),
PRIMARY KEY (image_id)
);


-- Create Orders Table
CREATE TABLE IF NOT EXISTS Orders(
order_id varchar(255) NOT NULL,
event_time varchar(255) NOT NULL,
customer_id varchar(255),
total_amount varchar(255),
PRIMARY KEY (order_id)
);


# extra table to keep weeks.
CREATE TABLE week(
date1 TIMESTAMP,
date2 TIMESTAMP,
week INT
);


--Views
 #borrowed logic from a forum on internet.

CREATE VIEW `customer_aquisition_week` AS
select
				a.customer_id,
				b.week,sum(cast(SUBSTRING_INDEX(SUBSTRING_INDEX(a.total_amount, ' ', 1), ' ', -1) AS DECIMAL(4,2)))/count(distinct(b.week))  AS amount
				from
				orders a,
				week b
				where (b.date1<=STR_TO_DATE(a.event_time,'%Y-%m-%d %H:%i:%s')
				and STR_TO_DATE(a.event_time,'%Y-%m-%d %H:%i:%s')<=b.date2)
			group by a.customer_id,b.week;


CREATE VIEW `customer_sitevisit` AS
            select
				a.customer_id,
				b.week,count(*)/count(distinct(b.week)) visits
			from sitevisit a,
			week b
			where (b.date1<=STR_TO_DATE(a.event_time,'%Y-%m-%d %H:%i:%s')
			and STR_TO_DATE(a.event_time,'%Y-%m-%d %H:%i:%s')<=b.date2)
			group by a.customer_id,b.week
			order by a.customer_id


CREATE VIEW customer_LTV AS
select
	d.last_name,
	d.adr_city,
	d.adr_state,
	d.customer_id,
	c.LTV
	from
(
	select
			a.customer_id,
			a.week,
			a.amount,
			b.visits,
			52*a.amount*b.visits*10 as LTV
			from customer_aquisition_week a, customer_sitevisit b
	where a.customer_id = b.customer_id
	and a.week = b.week
) c, customer d
where c.customer_id = d.customer_id
order by c.LTV desc