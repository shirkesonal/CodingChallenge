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

# used this TSQL script to genereate insert statements to pupulate WEEK table. - (i am more comfortable with TSQL) Insert statements are in pupulate_week.sql script.
/* declare @i int
set @i = 1
declare @day datetime = '2017-01-01'
declare @start datetime
declare @end datetime
while @i < 52
begin
select @start = DATEADD(day,7,@day)
select @end = DATEADD(day,7,@start)
select @day = @start
print( 'insert into week values (' + '''' + convert(varchar(250), @start,101) + '''' + ',' + '''' + convert(varchar(250),@end,101) + '''' + '1);')
select @i = @i+1
end */
/*
insert into week values ('2017-01-08 00:00:00.000','2017-01-15 00:00:00.000',1);
insert into week values ('2017-01-15 00:00:00.000','2017-01-22 00:00:00.000',2);
insert into week values ('2017-01-22 00:00:00.000','2017-01-29 00:00:00.000',3);
insert into week values ('2017-01-29 00:00:00.000','2017-02-05 00:00:00.000',4);
insert into week values ('2017-02-05 00:00:00.000','2017-02-12 00:00:00.000',5);
insert into week values ('2017-02-12 00:00:00.000','2017-02-19 00:00:00.000',6);
insert into week values ('2017-02-19 00:00:00.000','2017-02-26 00:00:00.000',7);
insert into week values ('2017-02-26 00:00:00.000','2017-03-05 00:00:00.000',8);
...................
*/


--Views


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
			52*a.amount*b.visits*10 as LTV  #borrowed this logic from a forum on internet.
			from customer_aquisition_week a, customer_sitevisit b
	where a.customer_id = b.customer_id
	and a.week = b.week
) c, customer d
where c.customer_id = d.customer_id
order by c.LTV desc